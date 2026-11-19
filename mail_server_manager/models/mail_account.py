# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import os
import re
import secrets
import shutil
import string
import tempfile
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import email_normalize

_logger = logging.getLogger(__name__)


class MailServerAccount(models.Model):
    """Modèle dédié pour les comptes email sur docker-mailserver"""

    _name = "mail.server.account"
    _inherit = ["mail.thread", "mail.server.manager.mixin"]
    _description = "Mail Server Account"
    _order = "email"
    _rec_name = "email"

    email = fields.Char(
        string="Email Address",
        required=True,
        index=True,
        tracking=True,
        help="The email address for this mail account (e.g., user@domain.com)",
    )
    user_id = fields.Many2one(
        "res.users",
        string="Odoo User",
        ondelete="set null",
        index=True,
        help="The Odoo user linked to this mail account. "
        "This user will be able to send emails using this address.",
    )
    mail_server_id = fields.Many2one(
        "ir.mail_server",
        string="Outgoing Mail Server (SMTP)",
        readonly=True,
        ondelete="set null",
        copy=False,
        help="The SMTP server automatically created for this account. "
        "Used for sending outgoing emails.",
    )
    fetchmail_server_id = fields.Many2one(
        "fetchmail.server",
        string="Incoming Mail Server (IMAP)",
        readonly=True,
        ondelete="set null",
        copy=False,
        help="The IMAP server automatically created for this account. "
        "Used for receiving incoming emails.",
    )

    active = fields.Boolean(
        default=True,
        help="If unchecked, the mail account is hidden but not deleted.",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("active", "Active"),
            ("suspended", "Suspended"),
            ("error", "Error"),
        ],
        default="draft",
        required=True,
        tracking=True,
        help="Current state of the mail account:\n"
        "- Draft: Account created but not yet provisioned\n"
        "- Active: Account is working normally\n"
        "- Suspended: Account temporarily disabled\n"
        "- Error: An error occurred during provisioning",
    )

    last_sync = fields.Datetime(
        readonly=True,
        help="Date and time of the last synchronization with the mail server.",
    )
    quota_mb = fields.Integer(
        default=1024,
        help="Maximum mailbox size in megabytes (default: 1024 MB = 1 GB).",
    )
    notes = fields.Text(
        help="Internal notes about this mail account (not visible to users).",
    )

    # Rate limiting fields
    last_password_reset = fields.Datetime(
        readonly=True,
        help="Timestamp of the last password reset (used for rate limiting).",
    )
    password_reset_count = fields.Integer(
        default=0,
        readonly=True,
        help="Number of password resets in the current rate limit window.",
    )

    # Email sending limits (anti-spam)
    daily_email_limit = fields.Integer(
        default=0,
        help="Maximum emails per day for this account. 0 = use system default.",
    )
    emails_sent_today = fields.Integer(
        default=0,
        readonly=True,
        help="Number of emails sent today (resets at midnight).",
    )
    last_email_count_reset = fields.Date(
        readonly=True,
        help="Date when the email count was last reset.",
    )

    # Unique email constraint (Odoo 19: prefer Python constraints)
    @api.constrains("email")
    def _check_email_unique(self):
        for record in self:
            if not record.email:
                continue
            if self.search_count(
                [("email", "=", record.email), ("id", "!=", record.id)], limit=1
            ):
                raise ValidationError(self.env._("Cette adresse email existe déjà."))

    # Regex stricte pour valider l'email et prévenir l'injection
    _EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    @api.constrains("email")
    def _check_email_format(self):
        """Validate email format and domain with strict regex to prevent injection"""
        for record in self:
            if not record.email:
                raise ValidationError(self.env._("Email address is required."))

            # SECURITY: Strict regex validation to prevent file injection
            if not self._EMAIL_REGEX.match(record.email):
                raise ValidationError(self.env._("Invalid email address format."))

            # Validate using Odoo's email_normalize
            normalized = email_normalize(record.email)
            if not normalized:
                raise ValidationError(self.env._("Invalid email address."))

            # Check domain part
            local_part, domain = record.email.split("@")
            if not local_part or not domain:
                raise ValidationError(
                    self.env._("Invalid email address: missing username.")
                )

            if "." not in domain:
                raise ValidationError(self.env._("Invalid domain: must contain a dot."))

    # Note: _get_mail_domain, _get_mail_config_path, _get_smtp_host,
    # _get_imap_host, _get_imap_port are inherited from mail.server.manager.mixin

    def _generate_password(self, length=16):
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return "".join(secrets.choice(alphabet) for _ in range(length))

    def _hash_password(self, password):
        """Hash password using SHA512-CRYPT format for docker-mailserver."""
        from passlib.hash import sha512_crypt

        return sha512_crypt.using(rounds=5000).hash(password)

    def _create_backup(self, filepath):
        """Create a backup of a file before modification.

        Returns the backup path or None if file doesn't exist.
        """
        if not os.path.exists(filepath):
            return None
        backup_path = f"{filepath}.bak"
        try:
            shutil.copy2(filepath, backup_path)
            _logger.debug("Created backup: %s", backup_path)
            return backup_path
        except Exception as e:
            _logger.warning("Could not create backup of %s: %s", filepath, e)
            return None

    def _atomic_write(self, filepath, content):
        """Write content to file atomically using temp file + rename.

        This prevents partial writes and data corruption.
        """
        dir_path = os.path.dirname(filepath)
        try:
            # Write to temp file in same directory (for atomic rename)
            fd, temp_path = tempfile.mkstemp(dir=dir_path, prefix=".tmp_")
            try:
                with os.fdopen(fd, "w") as f:
                    f.write(content)
                # Atomic rename
                os.rename(temp_path, filepath)
            except Exception:
                # Clean up temp file on error
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                raise
        except Exception as e:
            _logger.error("Atomic write failed for %s: %s", filepath, e)
            raise

    def _write_to_accounts_file(self, email, password_hash, action="add"):
        """Write to postfix-accounts.cf with atomic operations and backup.

        Uses atomic file writing to prevent data corruption and creates
        backups before destructive operations.
        """
        config_path = self._get_mail_config_path()
        accounts_file = os.path.join(config_path, "postfix-accounts.cf")

        try:
            if action == "add":
                line = f"{email}|{password_hash}\n"
                if not os.path.exists(accounts_file):
                    self._atomic_write(accounts_file, line)
                else:
                    with open(accounts_file) as f:
                        existing = f.read()
                    if email in existing:
                        raise UserError(self.env._("Email address already exists."))
                    # Append by rewriting atomically
                    self._atomic_write(accounts_file, existing + line)

            elif action == "update":
                if not os.path.exists(accounts_file):
                    raise UserError(self.env._("Mail configuration file not found."))
                # Create backup before update
                self._create_backup(accounts_file)
                with open(accounts_file) as f:
                    lines = f.readlines()
                new_lines = []
                found = False
                for line in lines:
                    if line.startswith(f"{email}|"):
                        new_lines.append(f"{email}|{password_hash}\n")
                        found = True
                    else:
                        new_lines.append(line)
                if not found:
                    raise UserError(self.env._("Email account not found."))
                self._atomic_write(accounts_file, "".join(new_lines))

            elif action == "delete":
                if not os.path.exists(accounts_file):
                    return
                # Create backup before delete
                self._create_backup(accounts_file)
                with open(accounts_file) as f:
                    lines = f.readlines()
                new_content = "".join(
                    line for line in lines if not line.startswith(f"{email}|")
                )
                self._atomic_write(accounts_file, new_content)

            _logger.info("Mail account %s: %s successful", action, email)

            # Update quota if adding or updating
            if action in ("add", "update"):
                self._write_quota_config(email)

        except PermissionError:
            _logger.error("Permission denied writing to %s", accounts_file)
            raise UserError(
                self.env._("Permission error writing to the mail file.")
            ) from None
        except UserError:
            raise
        except Exception as e:
            _logger.exception("Error in _write_to_accounts_file: %s", str(e))
            raise UserError(
                self.env._("Error during mail account modification.")
            ) from None

    def _write_quota_config(self, email):
        """Write quota configuration for dovecot.

        Creates/updates dovecot-quotas.cf with format: email:quota_bytes
        """
        config_path = self._get_mail_config_path()
        quota_file = os.path.join(config_path, "dovecot-quotas.cf")
        quota_bytes = self.quota_mb * 1024 * 1024  # Convert MB to bytes

        try:
            lines = []
            if os.path.exists(quota_file):
                with open(quota_file) as f:
                    lines = [
                        line
                        for line in f.readlines()
                        if not line.startswith(f"{email}:")
                    ]

            lines.append(f"{email}:{quota_bytes}\n")
            self._atomic_write(quota_file, "".join(lines))
            _logger.info("Quota set for %s: %d MB", email, self.quota_mb)
        except Exception as e:
            _logger.warning("Could not write quota for %s: %s", email, e)

    def _build_from_filter(self, user_personal_email=None):
        """
        Builds the from_filter string containing both internal and personal emails.

        Format: internal_email,personal_email
        Example: khalid.sahih@figacycles.com,khalid.sahih@gmail.com

        This allows the user to send emails using either address.
        """
        emails = [self.email]  # Internal email is always first

        # Add personal email if provided and different from internal
        if user_personal_email and user_personal_email != self.email:
            emails.append(user_personal_email)

        return ",".join(emails)

    def _create_smtp_server(self, password):
        """
        Creates the individual SMTP server for the user.

        This method follows Odoo's native approach:
        - Settings → Technical → Email → Outgoing Servers
        - from_filter: Contains both internal AND personal email

        The user will see this server in:
        Preferences → Specific Outgoing Server

        IMPORTANT: In Odoo 19, if owner_user_id is set with from_filter,
        Odoo validates that owner's email matches from_filter.
        We DON'T set owner_user_id to avoid validation conflicts.
        The from_filter contains both emails for maximum flexibility.
        """
        user_name = self.user_id.name if self.user_id else self.email.split("@")[0]
        user_personal_email = self.user_id.email if self.user_id else None

        # Build from_filter with both internal and personal email
        from_filter = self._build_from_filter(user_personal_email)

        return (
            self.env["ir.mail_server"]
            .sudo()
            .create(
                {
                    "name": f"SMTP - {user_name}",
                    "smtp_host": self._get_smtp_host(),
                    "smtp_port": 587,
                    "smtp_encryption": "starttls",
                    "smtp_user": self.email,
                    "smtp_pass": password,
                    "from_filter": from_filter,
                    "active": True,
                }
            )
        )

    def _update_smtp_from_filter(self, new_internal_email=None):
        """
        Updates the SMTP server's from_filter when internal email changes.
        Also updates smtp_user to match the new email.
        """
        if not self.mail_server_id:
            return

        internal_email = new_internal_email or self.email
        user_personal_email = self.user_id.email if self.user_id else None
        from_filter = self._build_from_filter(user_personal_email)

        self.mail_server_id.sudo().write(
            {
                "from_filter": from_filter,
                "smtp_user": internal_email,
            }
        )
        _logger.info("Updated SMTP from_filter for %s to %s", self.email, from_filter)

    def _update_smtp_user_email(self, old_personal_email, new_personal_email):
        """
        Updates the SMTP server's from_filter when user's personal email changes.

        This method is called silently with sudo() when a user changes their
        personal email, ensuring the from_filter list stays synchronized.

        Args:
            old_personal_email: The previous personal email (to be removed)
            new_personal_email: The new personal email (to be added)
        """
        if not self.mail_server_id:
            return

        # Get current from_filter and parse it
        current_filter = self.mail_server_id.from_filter or ""
        emails = [e.strip() for e in current_filter.split(",") if e.strip()]

        # Remove old personal email if present
        if old_personal_email and old_personal_email in emails:
            emails.remove(old_personal_email)

        # Ensure internal email is always first
        if self.email not in emails:
            emails.insert(0, self.email)
        elif emails[0] != self.email:
            emails.remove(self.email)
            emails.insert(0, self.email)

        # Add new personal email if different from internal
        if (
            new_personal_email
            and new_personal_email != self.email
            and new_personal_email not in emails
        ):
            emails.append(new_personal_email)

        new_filter = ",".join(emails)

        # Use sudo() to bypass permission checks - this is a system operation
        self.mail_server_id.sudo().write(
            {
                "from_filter": new_filter,
            }
        )
        _logger.info(
            "Updated SMTP from_filter for user email change: %s -> %s (filter: %s)",
            old_personal_email,
            new_personal_email,
            new_filter,
        )

    def _create_email_alias(self, forward_to_email):
        """
        Creates a forwarding alias in docker-mailserver.

        Emails received on the internal email will be copied to the personal email.
        This uses the postfix-virtual.cf file.
        """
        if not forward_to_email or forward_to_email == self.email:
            return

        config_path = self._get_mail_config_path()
        virtual_file = os.path.join(config_path, "postfix-virtual.cf")

        # Format: internal@domain external@otherdomain
        # This creates a copy, not a redirect
        alias_line = f"{self.email} {self.email},{forward_to_email}\n"

        try:
            existing_content = ""
            if os.path.exists(virtual_file):
                with open(virtual_file) as f:
                    existing_content = f.read()

            # Check if alias already exists
            if self.email in existing_content:
                # Update existing alias
                lines = existing_content.split("\n")
                new_lines = []
                for line in lines:
                    if line.startswith(f"{self.email} "):
                        new_lines.append(
                            f"{self.email} {self.email},{forward_to_email}"
                        )
                    else:
                        new_lines.append(line)
                with open(virtual_file, "w") as f:
                    f.write("\n".join(new_lines))
            else:
                # Add new alias
                with open(virtual_file, "a") as f:
                    f.write(alias_line)

            _logger.info(
                "Created email alias: %s -> copy to %s", self.email, forward_to_email
            )

        except PermissionError:
            _logger.warning("Permission denied creating alias in %s", virtual_file)
        except Exception:
            _logger.exception("Error creating email alias")

    def _delete_email_alias(self):
        """Removes the email alias from postfix-virtual.cf"""
        config_path = self._get_mail_config_path()
        virtual_file = os.path.join(config_path, "postfix-virtual.cf")

        if not os.path.exists(virtual_file):
            return

        try:
            with open(virtual_file) as f:
                lines = f.readlines()

            with open(virtual_file, "w") as f:
                for line in lines:
                    if not line.startswith(f"{self.email} "):
                        f.write(line)

            _logger.info("Deleted email alias for: %s", self.email)
        except Exception as e:
            _logger.warning("Error deleting email alias: %s", e)

    @api.model
    def _delete_email_alias_by_email(self, email):
        """Removes an email alias by email address."""
        config_path = self._get_mail_config_path()
        virtual_file = os.path.join(config_path, "postfix-virtual.cf")

        if not os.path.exists(virtual_file):
            return

        try:
            with open(virtual_file) as f:
                lines = f.readlines()

            with open(virtual_file, "w") as f:
                for line in lines:
                    if not line.startswith(f"{email} "):
                        f.write(line)

            _logger.info("Deleted email alias for: %s", email)
        except Exception as e:
            _logger.warning("Error deleting email alias for %s: %s", email, e)

    def _create_imap_server(self, password):
        """
        Creates the incoming IMAP server (fetchmail.server).

        Odoo will use this server to fetch mailboxes
        and route replies back to the Chatter.
        """
        return (
            self.env["fetchmail.server"]
            .sudo()
            .create(
                {
                    "name": f"IMAP - {self.email}",
                    "server_type": "imap",
                    "is_ssl": True,
                    "server": self._get_imap_host(),
                    "port": self._get_imap_port(),
                    "user": self.email,
                    "password": password,
                    "active": True,
                    "state": "draft",  # Requires manual confirmation
                }
            )
        )

    @api.model_create_multi
    def create(self, vals_list):
        """Create mail account with validation and proper cleanup on failure"""
        # Validate emails before creation
        for vals in vals_list:
            if "email" in vals:
                if not vals["email"] or "@" not in vals["email"]:
                    raise UserError(
                        self.env._("Cannot create mail account: Invalid email format.")
                    )

        records = super().create(vals_list)

        for record in records:
            mail_server = None
            fetchmail_server = None
            try:
                password = record._generate_password()
                password_hash = record._hash_password(password)

                # Créer dans docker-mailserver
                record._write_to_accounts_file(record.email, password_hash, "add")

                # Créer le serveur SMTP (Sortant)
                mail_server = record._create_smtp_server(password)
                record.mail_server_id = mail_server.id

                # Créer le serveur IMAP (Entrant)
                fetchmail_server = record._create_imap_server(password)
                record.fetchmail_server_id = fetchmail_server.id

                record.state = "active"
                record.last_sync = fields.Datetime.now()

                # Create forwarding alias if user has a personal email
                if record.user_id and record.user_id.email:
                    record._create_email_alias(record.user_id.email)

                _logger.info("Created mail account: %s", record.email)

            except Exception as e:
                _logger.exception("Failed to create mail account %s", record.email)

                # SECURITY FIX: Cleanup created resources on failure
                try:
                    # Delete SMTP server if created
                    if mail_server:
                        mail_server.sudo().unlink()
                        _logger.info(
                            "Cleaned up SMTP server for failed account %s", record.email
                        )
                    # Delete IMAP server if created
                    if fetchmail_server:
                        fetchmail_server.sudo().unlink()
                        _logger.info(
                            "Cleaned up IMAP server for failed account %s", record.email
                        )
                    # Delete from postfix-accounts.cf
                    record._write_to_accounts_file(record.email, "", "delete")
                except Exception as cleanup_error:
                    _logger.warning(
                        "Cleanup failed for %s: %s", record.email, cleanup_error
                    )

                record.state = "error"
                raise UserError(self.env._("Failed to create mail account.")) from e

        # Q35: Send reminder notification for IMAP server confirmation
        if records and self.env.context.get("show_imap_reminder", True):
            try:
                imap_reminder_accounts = records.filtered(
                    lambda r: r.fetchmail_server_id
                    and r.fetchmail_server_id.state == "draft"
                )
                if imap_reminder_accounts:
                    self.env["bus.bus"]._sendone(
                        self.env.user.partner_id,
                        "simple_notification",
                        {
                            "type": "warning",
                            "title": self.env._("IMAP Server Configuration Reminder"),
                            "message": self.env._(
                                "Please confirm IMAP server(s) in "
                                "Settings → Technical → Incoming Mail Servers."
                            ),
                            "sticky": True,
                        },
                    )
            except Exception as e:
                # Non-critical notification failure should not block account creation
                _logger.warning("Failed to send IMAP reminder notification: %s", e)

        return records

    def unlink(self):
        """Delete mail account with proper cleanup (optimized batch operations)"""
        if not self:
            return super().unlink()

        # OPTIMIZATION: Collect all servers to delete in batch
        smtp_servers_to_delete = self.env["ir.mail_server"]
        imap_servers_to_delete = self.env["fetchmail.server"]
        emails_to_delete = []

        for record in self:
            emails_to_delete.append(record.email)
            if record.mail_server_id:
                smtp_servers_to_delete |= record.mail_server_id
            if record.fetchmail_server_id:
                imap_servers_to_delete |= record.fetchmail_server_id

        # Delete from docker-mailserver
        for email in emails_to_delete:
            try:
                self._write_to_accounts_file(email, "", "delete")
                # Also delete email alias
                self.env["mail.server.account"]._delete_email_alias_by_email(email)
            except Exception as e:
                _logger.warning(
                    "Failed to delete from postfix-accounts: %s - %s", email, e
                )

        # Batch delete SMTP servers
        if smtp_servers_to_delete:
            try:
                smtp_servers_to_delete.sudo().unlink()
                _logger.info(
                    "Batch deleted %d SMTP servers", len(smtp_servers_to_delete)
                )
            except Exception as e:
                _logger.warning("Failed to batch delete SMTP servers: %s", e)

        # Batch delete IMAP servers
        if imap_servers_to_delete:
            try:
                imap_servers_to_delete.sudo().unlink()
                _logger.info(
                    "Batch deleted %d IMAP servers", len(imap_servers_to_delete)
                )
            except Exception as e:
                _logger.warning("Failed to batch delete IMAP servers: %s", e)

        _logger.info("Deleted %d mail accounts", len(self))

        return super().unlink()

    def action_reset_password(self):
        """Réinitialise le mot de passe du compte mail avec rate limiting"""
        self.ensure_one()

        # RATE LIMITING: Check if too many resets in the last hour
        one_hour_ago = fields.Datetime.now() - timedelta(hours=1)
        if self.last_password_reset and self.last_password_reset > one_hour_ago:
            if self.password_reset_count >= 3:
                raise UserError(
                    self.env._(
                        "Password reset rate limit exceeded.\n\n"
                        "You can only reset the password 3 times per hour. "
                        "Please wait before trying again."
                    )
                )
            self.password_reset_count += 1
        else:
            self.password_reset_count = 1

        password = self._generate_password()
        password_hash = self._hash_password(password)

        self._write_to_accounts_file(self.email, password_hash, "update")

        if self.mail_server_id:
            self.mail_server_id.sudo().write({"smtp_pass": password})

        if self.fetchmail_server_id:
            self.fetchmail_server_id.sudo().write({"password": password})

        self.last_sync = fields.Datetime.now()
        self.last_password_reset = fields.Datetime.now()

        # Q25: Open secure wizard modal instead of sticky notification
        wizard = self.env["mail.server.password.wizard"].create(
            {
                "password": password,
                "mail_account_id": self.id,
            }
        )

        return {
            "name": self.env._("Password Generated"),
            "type": "ir.actions.act_window",
            "res_model": "mail.server.password.wizard",
            "res_id": wizard.id,
            "view_mode": "form",
            "target": "new",
        }

    def action_suspend(self):
        """Suspend le compte mail"""
        for record in self:
            if record.mail_server_id:
                record.mail_server_id.sudo().write({"active": False})
            record.state = "suspended"
        return True

    def action_activate(self):
        """Réactive le compte mail"""
        for record in self:
            if record.mail_server_id:
                record.mail_server_id.sudo().write({"active": True})
            record.state = "active"
        return True

    def action_sync_from_server(self):
        """Synchronise les comptes depuis le fichier postfix-accounts.cf"""
        config_path = self._get_mail_config_path()
        accounts_file = os.path.join(config_path, "postfix-accounts.cf")

        if not os.path.exists(accounts_file):
            raise UserError(self.env._("Fichier de configuration mail introuvable."))

        with open(accounts_file) as f:
            lines = f.readlines()

        existing_emails = set(self.search([], limit=10000).mapped("email"))
        synced = 0

        for line in lines:
            if "|" in line:
                email = line.split("|")[0].strip()
                if email and email not in existing_emails:
                    self.create({"email": email, "state": "active"})
                    synced += 1

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": self.env._("Sync Completed"),
                "message": self.env._("Sync completed successfully."),
                "type": "success",
            },
        }

    def action_open_smtp_server(self):
        """Opens the associated SMTP server form"""
        self.ensure_one()
        if not self.mail_server_id:
            raise UserError(self.env._("No SMTP server associated with this account."))
        return {
            "type": "ir.actions.act_window",
            "res_model": "ir.mail_server",
            "res_id": self.mail_server_id.id,
            "view_mode": "form",
            "target": "current",
        }

    def action_open_imap_server(self):
        """Opens the associated IMAP server form"""
        self.ensure_one()
        if not self.fetchmail_server_id:
            raise UserError(self.env._("No IMAP server associated with this account."))
        return {
            "type": "ir.actions.act_window",
            "res_model": "fetchmail.server",
            "res_id": self.fetchmail_server_id.id,
            "view_mode": "form",
            "target": "current",
        }

    def action_recover_from_error(self):
        """Attempts to recover accounts from error state.

        This method will try to re-provision the mail account by:
        1. Regenerating password
        2. Recreating missing SMTP/IMAP servers
        3. Updating the postfix-accounts.cf file
        """
        for record in self:
            # Check if recovery is needed: error state OR missing servers
            missing_servers = (
                not record.mail_server_id or not record.fetchmail_server_id
            )
            if record.state != "error" and not missing_servers:
                continue

            try:
                password = record._generate_password()
                password_hash = record._hash_password(password)

                # Update or create in docker-mailserver
                try:
                    record._write_to_accounts_file(
                        record.email, password_hash, "update"
                    )
                except UserError:
                    # Account doesn't exist, create it
                    record._write_to_accounts_file(record.email, password_hash, "add")

                # Recreate SMTP server if missing
                if not record.mail_server_id:
                    mail_server = record._create_smtp_server(password)
                    record.mail_server_id = mail_server.id
                else:
                    record.mail_server_id.sudo().write({"smtp_pass": password})

                # Recreate IMAP server if missing
                if not record.fetchmail_server_id:
                    fetchmail_server = record._create_imap_server(password)
                    record.fetchmail_server_id = fetchmail_server.id
                else:
                    record.fetchmail_server_id.sudo().write({"password": password})

                record.state = "active"
                record.last_sync = fields.Datetime.now()

                _logger.info("Recovered mail account from error: %s", record.email)

            except Exception as e:
                _logger.exception("Failed to recover mail account %s", record.email)
                raise UserError(self.env._("Failed to recover mail account.")) from e

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": self.env._("Recovery Complete"),
                "message": self.env._(
                    "Account(s) successfully recovered and repaired."
                ),
                "type": "success",
            },
        }

    def action_fix_smtp_owner(self):
        """Fix SMTP servers with owner_user_id causing Odoo 19 errors.

        Removes owner_user_id and sets from_filter properly.
        """
        fixed_count = 0
        for record in self:
            if record.mail_server_id:
                # Build from_filter with both internal and personal email
                user_personal_email = record.user_id.email if record.user_id else None
                from_filter = record._build_from_filter(user_personal_email)

                record.mail_server_id.sudo().write(
                    {
                        "owner_user_id": False,
                        "from_filter": from_filter,
                    }
                )
                fixed_count += 1
                _logger.info(
                    "Fixed SMTP server for: %s (filter: %s)",
                    record.email,
                    from_filter,
                )

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": self.env._("SMTP Servers Fixed"),
                "message": self.env._("SMTP servers updated successfully."),
                "type": "success",
            },
        }

    @api.model
    def action_fix_all_smtp_owners(self):
        """
        Fix ALL SMTP servers created by this module.
        Sets from_filter to include both internal AND user's personal email.
        This is a batch operation for administrators.
        """
        accounts = self.search([("mail_server_id", "!=", False)])
        fixed_count = 0

        for account in accounts:
            # Build from_filter with both internal and personal email
            user_personal_email = account.user_id.email if account.user_id else None
            from_filter = account._build_from_filter(user_personal_email)

            account.mail_server_id.sudo().write(
                {
                    "owner_user_id": False,
                    "from_filter": from_filter,
                }
            )
            fixed_count += 1
            _logger.info(
                "Batch fixed SMTP server for: %s (filter: %s)",
                account.email,
                from_filter,
            )

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": self.env._("Batch Fix Complete"),
                "message": self.env._("SMTP servers fixed successfully."),
                "type": "success",
            },
        }
