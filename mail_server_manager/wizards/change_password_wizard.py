# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ChangeMailPasswordWizard(models.TransientModel):
    """Secure wizard for users to change their mail password.

    Requires verification of Odoo password before allowing password change.
    """

    _name = "mail.password.change.wizard"
    _description = "Change Mail Password Wizard"

    mail_account_id = fields.Many2one(
        "mail.server.account",
        string="Mail Account",
        required=True,
        readonly=True,
    )
    email = fields.Char(
        related="mail_account_id.email",
        string="Email Address",
        readonly=True,
    )
    current_odoo_password = fields.Char(
        required=True,
        help="Enter your current Odoo password to verify your identity.",
    )
    new_mail_password = fields.Char(
        help="Leave empty to auto-generate a secure password.",
    )
    confirm_mail_password = fields.Char(
        help="Re-enter the new password to confirm.",
    )
    generated_password = fields.Char(
        readonly=True,
    )
    state = fields.Selection(
        [
            ("verify", "Verify Identity"),
            ("change", "Change Password"),
            ("done", "Done"),
        ],
        default="verify",
        readonly=True,
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        # Get user's mail account
        user = self.env.user
        if user.mail_account_id:
            res["mail_account_id"] = user.mail_account_id.id
        return res

    def action_verify_password(self):
        """Verify the user's Odoo password before allowing password change."""
        self.ensure_one()

        _logger.warning("=== PASSWORD VERIFICATION START ===")
        _logger.warning("Password field value: %s", repr(self.current_odoo_password))

        if not self.current_odoo_password:
            _logger.warning("No password provided!")
            raise ValidationError(
                self.env._("Please enter your current Odoo password.")
            )

        # Simple direct database verification (most reliable)
        user = self.create_uid

        try:
            self.env.cr.execute(
                "SELECT COALESCE(password, '') FROM res_users WHERE id=%s", [user.id]
            )
            stored_hash = self.env.cr.fetchone()[0]

            if not stored_hash:
                raise ValidationError(self.env._("No password set for this user."))

            # Debug: show hash format
            _logger.warning("=== PASSWORD VERIFICATION DEBUG ===")
            _logger.warning("User ID: %s, Login: %s", user.id, user.login)
            _logger.warning(
                "Stored hash format: %s...", stored_hash[:30] if stored_hash else "None"
            )
            _logger.warning("Password length: %d", len(self.current_odoo_password))
            _logger.warning(
                "Testing password: %s...",
                self.current_odoo_password[:2]
                + "*" * (len(self.current_odoo_password) - 2)
                if len(self.current_odoo_password) > 2
                else "***",
            )
            _logger.warning("Hash length: %d", len(stored_hash))
            _logger.warning(
                "Hash starts with: %s", stored_hash[:10] if stored_hash else "None"
            )
            _logger.warning(
                "Hash ends with: %s", stored_hash[-10:] if stored_hash else "None"
            )

            # Check if hash starts with $pbkdf2-sha512$ (Odoo 19 default)
            if stored_hash.startswith("$pbkdf2-sha512$"):
                _logger.warning("Detected pbkdf2-sha512 hash format")
                # Try with the exact scheme name Odoo uses
                from passlib.context import CryptContext

                crypt_context = CryptContext(schemes=["pbkdf2_sha512"])
                if crypt_context.verify(self.current_odoo_password, stored_hash):
                    _logger.warning("Password OK (pbkdf2_sha512) for %s", user.login)
                    # Password verified, move to change step
                    self.state = "change"
                    return {
                        "type": "ir.actions.act_window",
                        "res_model": self._name,
                        "res_id": self.id,
                        "view_mode": "form",
                        "target": "new",
                    }
                else:
                    _logger.warning(
                        "pbkdf2_sha512 verification failed for user %s", user.login
                    )
                    raise ValidationError(
                        self.env._("Incorrect password. Please try again.")
                    )

            # Try direct string comparison first (for plaintext or simple cases)
            if self.current_odoo_password == stored_hash:
                _logger.warning(
                    "Direct string comparison successful for user %s", user.login
                )
            else:
                _logger.warning("Trying other hash schemes...")
                # Check all possible hash schemes Odoo might use
                from passlib.context import CryptContext

                # Try each scheme individually for better debugging
                schemes = ["pbkdf2_sha512", "sha512_crypt", "bcrypt", "plaintext"]

                for scheme in schemes:
                    _logger.warning("Trying scheme: %s", scheme)
                    try:
                        crypt_context = CryptContext(schemes=[scheme])
                        if crypt_context.verify(
                            self.current_odoo_password, stored_hash
                        ):
                            _logger.warning(
                                "Password OK for %s using %s",
                                user.login,
                                scheme,
                            )
                            break
                        else:
                            _logger.warning(
                                "Scheme %s: hash mismatch for user %s",
                                scheme,
                                user.login,
                            )
                    except Exception as e:
                        _logger.warning(
                            "Scheme %s exception for user %s: %s",
                            scheme,
                            user.login,
                            str(e),
                        )
                else:
                    _logger.warning("All hash schemes failed for user %s", user.login)
                    raise ValidationError(
                        self.env._("Incorrect password. Please try again.")
                    )

        except ValidationError:
            raise
        except Exception as e:
            _logger.exception("Password verification error: %s", e)
            raise ValidationError(
                self.env._("Incorrect password. Please try again.")
            ) from e

        # Password verified, move to change step
        self.state = "change"

        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def action_change_password(self):
        """Change the mail password after verification."""
        self.ensure_one()

        if self.state != "change":
            raise UserError(self.env._("Please verify your identity first."))

        mail_account = self.mail_account_id.sudo()

        # Determine new password
        if self.new_mail_password:
            # User provided a password
            if self.new_mail_password != self.confirm_mail_password:
                raise ValidationError(self.env._("Passwords do not match."))

            # Validate password strength
            if len(self.new_mail_password) < 8:
                raise ValidationError(
                    self.env._("Password must be at least 8 characters long.")
                )

            new_password = self.new_mail_password
        else:
            # Generate a secure password
            new_password = mail_account._generate_password()

        # Hash and update password
        password_hash = mail_account._hash_password(new_password)
        mail_account._write_to_accounts_file(
            mail_account.email, password_hash, action="update"
        )

        # Update SMTP server password
        if mail_account.mail_server_id:
            mail_account.mail_server_id.sudo().write({"smtp_pass": new_password})

        # Store generated password for display
        self.generated_password = new_password
        self.state = "done"

        _logger.info(
            "User %s changed mail password for account %s",
            self.env.user.login,
            mail_account.email,
        )

        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def action_close(self):
        """Close the wizard."""
        return {"type": "ir.actions.act_window_close"}
