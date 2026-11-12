# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = ["res.users", "mail.server.manager.mixin"]
    _name = "res.users"

    create_mailbox = fields.Boolean(
        help="If checked, a mailbox will be automatically created for this user",
        default=False,
    )
    mail_account_id = fields.Many2one(
        "mail.server.account",
        readonly=True,
        ondelete="set null",
    )
    internal_email = fields.Char(
        compute="_compute_internal_email",
        store=True,
        help="Internal email address for this user (from Mail Server Manager)",
    )
    mailbox_created = fields.Boolean(
        compute="_compute_mailbox_created",
        store=True,
    )

    # Email client configuration fields (computed for display in preferences)
    smtp_server = fields.Char(
        string="SMTP Server",
        compute="_compute_mail_config",
    )
    smtp_port = fields.Integer(
        string="SMTP Port",
        compute="_compute_mail_config",
    )
    smtp_encryption = fields.Char(
        string="SMTP Encryption",
        compute="_compute_mail_config",
    )
    imap_server = fields.Char(
        string="IMAP Server",
        compute="_compute_mail_config",
    )
    imap_port = fields.Integer(
        string="IMAP Port",
        compute="_compute_mail_config",
    )
    imap_encryption = fields.Char(
        string="IMAP Encryption",
        compute="_compute_mail_config",
    )

    @api.depends("mail_account_id", "mail_account_id.email")
    def _compute_internal_email(self):
        for user in self:
            user.internal_email = (
                user.mail_account_id.email if user.mail_account_id else False
            )

    @api.depends("mail_account_id")
    def _compute_mailbox_created(self):
        for user in self:
            user.mailbox_created = bool(user.mail_account_id)

    def _compute_mail_config(self):
        """Compute email client configuration for display."""
        ICP = self.env["ir.config_parameter"].sudo()
        smtp_host = ICP.get_param("mail_server_manager.smtp_host", "mail")
        smtp_port = int(ICP.get_param("mail_server_manager.smtp_port", 587))
        smtp_enc = ICP.get_param("mail_server_manager.smtp_encryption", "starttls")
        imap_host = ICP.get_param("mail_server_manager.imap_host", "mail")
        imap_port = int(ICP.get_param("mail_server_manager.imap_port", 993))
        imap_enc = ICP.get_param("mail_server_manager.imap_encryption", "ssl")

        encryption_labels = {
            "none": "None",
            "starttls": "STARTTLS",
            "ssl": "SSL/TLS",
        }

        for user in self:
            user.smtp_server = smtp_host
            user.smtp_port = smtp_port
            user.smtp_encryption = encryption_labels.get(smtp_enc, smtp_enc)
            user.imap_server = imap_host
            user.imap_port = imap_port
            user.imap_encryption = encryption_labels.get(imap_enc, imap_enc)

    # Note: _get_mail_domain, _get_auto_create_mailbox are now in the mixin

    @api.model_create_multi
    def create(self, vals_list):
        # Vérifier si création auto est activée
        auto_create = self._get_auto_create_mailbox()

        for vals in vals_list:
            if auto_create and "create_mailbox" not in vals:
                vals["create_mailbox"] = True

        users = super().create(vals_list)

        for user in users.filtered("create_mailbox"):
            if not user.mail_account_id:
                user._create_mail_account()

        return users

    def write(self, vals):
        # Track email changes for users with mail accounts
        old_emails = {}
        if "email" in vals:
            for user in self.filtered("mail_account_id"):
                old_emails[user.id] = user.email

        result = super().write(vals)

        # Si on active "Créer boîte mail" après la création
        if vals.get("create_mailbox"):
            for user in self.filtered(lambda u: not u.mail_account_id):
                user._create_mail_account()

        # Update email alias and SMTP from_filter when user's personal email changes
        if "email" in vals and old_emails:
            for user in self.filtered("mail_account_id"):
                old_email = old_emails.get(user.id)
                new_email = user.email
                if old_email != new_email and user.mail_account_id:
                    # Use sudo() to bypass permission checks
                    # System must update SMTP from_filter silently
                    mail_account = user.mail_account_id.sudo()

                    # Update the forwarding alias to the new personal email
                    mail_account._create_email_alias(new_email)

                    # Update SMTP from_filter: remove old email, add new one
                    mail_account._update_smtp_user_email(old_email, new_email)

                    _logger.info(
                        "Updated email config for user %s: %s -> %s",
                        user.login,
                        old_email,
                        new_email,
                    )

        return result

    def _generate_internal_email_prefix(self):
        """
        Generates a professional email prefix based on:
        1. User's personal email prefix (if exists)
        2. User's name (firstname.lastname format)
        3. Fallback to login
        """
        import re
        import unicodedata

        def normalize(text):
            """Remove accents and special characters"""
            text = unicodedata.normalize("NFD", text)
            text = "".join(c for c in text if unicodedata.category(c) != "Mn")
            text = re.sub(r"[^a-zA-Z0-9._-]", "", text.lower())
            return text

        # Option 1: Use personal email prefix if available
        if self.email and "@" in self.email:
            prefix = self.email.split("@")[0]
            # Clean the prefix
            prefix = normalize(prefix)
            if prefix:
                return prefix

        # Option 2: Use user name (firstname.lastname)
        if self.name:
            parts = self.name.strip().split()
            if len(parts) >= 2:
                # firstname.lastname
                firstname = normalize(parts[0])
                lastname = normalize(parts[-1])
                if firstname and lastname:
                    return f"{firstname}.{lastname}"
            elif len(parts) == 1:
                return normalize(parts[0])

        # Fallback: Use login
        return normalize(self.login) or "user"

    def _create_mail_account(self):
        """Creates the mail account for this user"""
        self.ensure_one()
        domain = self._get_mail_domain()
        prefix = self._generate_internal_email_prefix()
        email = f"{prefix}@{domain}"

        # Check for uniqueness and add suffix if needed
        existing = (
            self.env["mail.server.account"].sudo().search([("email", "=", email)])
        )
        if existing:
            # Add numeric suffix
            counter = 1
            while (
                self.env["mail.server.account"]
                .sudo()
                .search([("email", "=", f"{prefix}{counter}@{domain}")])
            ):
                counter += 1
            email = f"{prefix}{counter}@{domain}"

        try:
            mail_account = self.env["mail.server.account"].create(
                {
                    "email": email,
                    "user_id": self.id,
                }
            )
            self.mail_account_id = mail_account.id
            _logger.info("Created mail account %s for user %s", email, self.login)
        except Exception as e:
            _logger.exception("Failed to create mail account for user %s", self.login)
            raise UserError(self.env._("Failed to create mail account.")) from e

    def action_create_mailbox(self):
        """Manual action to create a mailbox"""
        for user in self:
            if not user.mail_account_id:
                user._create_mail_account()
        return True

    def action_view_mail_account(self):
        """Opens the associated mail account"""
        self.ensure_one()
        if not self.mail_account_id:
            raise UserError(self.env._("No mail account associated with this user."))
        return {
            "type": "ir.actions.act_window",
            "res_model": "mail.server.account",
            "res_id": self.mail_account_id.id,
            "view_mode": "form",
            "target": "current",
        }

    def action_change_mail_password(self):
        """Opens the secure password change wizard for the user's mail account."""
        self.ensure_one()
        if not self.mail_account_id:
            raise UserError(self.env._("No mail account associated with this user."))

        return {
            "type": "ir.actions.act_window",
            "name": self.env._("Change Mail Password"),
            "res_model": "mail.password.change.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_mail_account_id": self.mail_account_id.id,
            },
        }

    def _get_smtp_config(self):
        """Returns SMTP configuration for email client setup."""
        self.ensure_one()
        ICP = self.env["ir.config_parameter"].sudo()
        return {
            "server": ICP.get_param("mail_server_manager.smtp_host", "mail"),
            "port": int(ICP.get_param("mail_server_manager.smtp_port", 587)),
            "encryption": ICP.get_param(
                "mail_server_manager.smtp_encryption", "starttls"
            ),
            "username": self.internal_email or "",
        }

    def _get_imap_config(self):
        """Returns IMAP configuration for email client setup."""
        self.ensure_one()
        ICP = self.env["ir.config_parameter"].sudo()
        return {
            "server": ICP.get_param("mail_server_manager.imap_host", "mail"),
            "port": int(ICP.get_param("mail_server_manager.imap_port", 993)),
            "encryption": ICP.get_param("mail_server_manager.imap_encryption", "ssl"),
            "username": self.internal_email or "",
        }
