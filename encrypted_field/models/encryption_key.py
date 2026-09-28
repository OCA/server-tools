import logging

from odoo import _, api, models
from odoo.exceptions import UserError
from odoo.tools import config

_logger = logging.getLogger(__name__)


class EncryptionKeyMixin(models.AbstractModel):
    """Mixin providing encryption key utilities."""

    _name = "pb.encryption.key.mixin"
    _description = "Encryption Key Mixin"

    @api.model
    def _get_encryption_key(self):
        """Get the encryption key from configuration."""
        key = config.get("encryption_key")
        if not key:
            raise UserError(
                _(
                    "No encryption key configured. Add 'encryption_key' to your "
                    "Odoo configuration file."
                )
            )
        return key

    @api.model
    def _validate_encryption_key(self, key):
        """Validate that a key is a valid Fernet key."""
        try:
            from cryptography.fernet import Fernet

            Fernet(key.encode() if isinstance(key, str) else key)
            return True
        except Exception as e:
            raise UserError(
                _("Invalid encryption key: %(error)s") % {"error": str(e)}
            ) from e

    @api.model
    def _generate_encryption_key(self):
        """Generate a new Fernet encryption key."""
        try:
            from cryptography.fernet import Fernet

            return Fernet.generate_key().decode()
        except ImportError as err:
            raise UserError(
                _(
                    "The 'cryptography' package is required. "
                    "Install it with: pip install cryptography"
                )
            ) from err

    @api.model
    def check_encryption_configured(self):
        """Check if encryption is properly configured."""
        try:
            key = self._get_encryption_key()
            self._validate_encryption_key(key)
            return True
        except UserError:
            return False
