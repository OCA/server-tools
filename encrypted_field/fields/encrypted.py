import logging

from odoo import _, fields
from odoo.exceptions import UserError
from odoo.tools import config

_logger = logging.getLogger(__name__)

# Lazy import cryptography to allow module loading even if not installed
_fernet = None
_key_version = None  # Track which version of key we have cached


def _get_key_version():
    """Get the current key version from database (shared across all workers)."""
    try:
        from odoo import SUPERUSER_ID, api
        from odoo.modules.registry import Registry

        db_name = config.get("db_name")
        if db_name:
            registry = Registry(db_name)
            with registry.cursor() as cr:
                env = api.Environment(cr, SUPERUSER_ID, {})
                version = (
                    env["ir.config_parameter"]
                    .sudo()
                    .get_param("encryption.key_version", "0")
                )
                return version
    except Exception:
        return "0"


def _reload_config():
    """Force reload of config file to get updated encryption_key."""
    # Re-read the specific option from the config file
    import configparser

    config_file = config.rcfile
    if config_file:
        try:
            parser = configparser.ConfigParser()
            parser.read(config_file)
            if parser.has_option("options", "encryption_key"):
                new_key = parser.get("options", "encryption_key")
                config["encryption_key"] = new_key
                return new_key
        except Exception as e:
            _logger.warning("Failed to reload config: %s", e)
    return config.get("encryption_key")


def _get_fernet():
    """Get or create Fernet instance with key from config."""
    global _fernet, _key_version

    # Check if key version changed (another worker rotated the key)
    current_version = _get_key_version()
    if _fernet is not None and _key_version == current_version:
        return _fernet

    # Version changed or first load - reload config and recreate fernet
    if _key_version is not None and _key_version != current_version:
        _logger.info(
            "Encryption key version changed (%s -> %s), reloading config",
            _key_version,
            current_version,
        )
        key = _reload_config()
    else:
        key = config.get("encryption_key")

    try:
        from cryptography.fernet import Fernet
    except ImportError as err:
        raise UserError(
            _(
                "The 'cryptography' package is required for encrypted fields. "
                "Install it with: pip install cryptography"
            )
        ) from err

    if not key:
        raise UserError(
            _(
                "No encryption key configured. Add 'encryption_key' to your "
                "Odoo configuration file. Generate a key with: "
                'python -c "from cryptography.fernet import Fernet; '
                'print(Fernet.generate_key().decode())"'
            )
        )

    try:
        _fernet = Fernet(key.encode() if isinstance(key, str) else key)
        _key_version = current_version
    except Exception as e:
        raise UserError(
            _(
                "Invalid encryption key in configuration. "
                "Key must be a valid Fernet key (32 url-safe base64-encoded bytes). "
                "Error: %(error)s"
            )
            % {"error": str(e)}
        ) from e

    return _fernet


def bump_key_version(env):
    """Increment the key version in database. Call after updating config file."""
    import time

    new_version = str(int(time.time()))
    env["ir.config_parameter"].sudo().set_param("encryption.key_version", new_version)
    return new_version


def encrypt_value(value):
    """Encrypt a string value."""
    if value is None:
        return None
    fernet = _get_fernet()
    return fernet.encrypt(value.encode()).decode()


def decrypt_value(value):
    """Decrypt an encrypted string value."""
    if value is None:
        return None
    fernet = _get_fernet()
    try:
        return fernet.decrypt(value.encode()).decode()
    except Exception as e:
        _logger.error("Failed to decrypt value: %s", e)
        raise UserError(
            _("Failed to decrypt value. The encryption key may have changed.")
        ) from e


def is_encrypted_value(value):
    """Check if a value looks like a Fernet-encrypted token.

    Fernet tokens are base64-encoded and start with version byte 0x80,
    which encodes to 'gA' in base64.
    """
    if not isinstance(value, str):
        return False
    # Fernet tokens start with 'gA' (version byte 0x80) and are base64
    # They're typically 100+ chars for even short plaintext
    return value.startswith("gA") and len(value) > 50


# Built-in format patterns
FORMAT_PATTERNS = {
    "ssn": {
        "pattern": "###-##-####",
        "strip": "-",  # Characters to strip when storing
    },
    "phone": {
        "pattern": "(###) ###-####",
        "strip": "()- ",
    },
    "ein": {
        "pattern": "##-#######",
        "strip": "-",
    },
    "credit_card": {
        "pattern": "####-####-####-####",
        "strip": "- ",
    },
}


def strip_format(value, format_name):
    """Remove formatting characters from a value for storage."""
    if not value or not format_name:
        return value

    fmt = FORMAT_PATTERNS.get(format_name)
    if not fmt:
        return value

    # Strip the specified characters
    result = value
    for char in fmt.get("strip", ""):
        result = result.replace(char, "")
    return result


def apply_format(value, format_name):
    """Apply formatting to a raw value for display."""
    if not value or not format_name:
        return value

    fmt = FORMAT_PATTERNS.get(format_name)
    if not fmt:
        return value

    pattern = fmt["pattern"]

    # Strip any existing formatting first
    clean_value = strip_format(value, format_name)

    # Apply the pattern
    result = []
    value_idx = 0
    for char in pattern:
        if value_idx >= len(clean_value):
            break
        if char == "#":
            result.append(clean_value[value_idx])
            value_idx += 1
        else:
            result.append(char)

    # Append any remaining characters (if value is longer than pattern)
    if value_idx < len(clean_value):
        result.append(clean_value[value_idx:])

    return "".join(result)


class Encrypted(fields.Char):
    """
    Encrypted field wrapper for storing sensitive data.

    Usage:
        ssn = Encrypted(string='SSN')
        tax_id = Encrypted(
            string='Tax ID',
            groups='account.group_account_manager',
            mask='last4',
        )

    The field stores encrypted data in the database as TEXT.

    Parameters:
        groups: Comma-separated group XML IDs that can see decrypted values
        mask: Masking mode for users without full access:
            - 'last4': Show last 4 characters (e.g., '***-**-6789')
            - 'first4': Show first 4 characters
            - 'full': Full masking (e.g., '********')
            - callable: Custom function(value) -> masked_value
        audit: If True, log access to decrypted values (default: True)

    WARNING: Search/filter operations on encrypted fields are not supported
    and will raise an error.
    """

    # Override column type to ensure we have enough space for encrypted data
    column_type = ("text", "TEXT")

    encrypt_groups = None
    mask = "full"
    audit = True
    format_pattern = None

    def __init__(
        self,
        string=None,
        encrypt_groups=None,
        mask="full",
        audit=True,
        format_pattern=None,
        **kwargs,
    ):
        self.encrypt_groups = encrypt_groups
        self.mask = mask
        self.audit = audit
        self.format_pattern = format_pattern
        # Disable tracking by default - don't log sensitive data in chatter
        kwargs.setdefault("tracking", False)
        # Disable copy by default - don't duplicate sensitive data
        kwargs.setdefault("copy", False)
        super().__init__(string=string, **kwargs)

    def _format_value(self, value):
        """Apply formatting to a value for display."""
        if not value or not self.format_pattern:
            return value
        return apply_format(value, self.format_pattern)

    def _strip_format(self, value):
        """Strip formatting from a value for storage."""
        if not value or not self.format_pattern:
            return value
        return strip_format(value, self.format_pattern)

    def _user_has_access(self, env):
        """Check if current user has access to decrypted values."""
        if not self.encrypt_groups:
            return True
        user = env.user
        for group_xmlid in self.encrypt_groups.split(","):
            group_xmlid = group_xmlid.strip()
            if user.has_group(group_xmlid):
                return True
        return False

    def _mask_last4(self, formatted):
        """Mask all but last 4 alphanumeric characters."""
        if len(formatted) <= 4:
            return formatted
        # Count non-format characters from the end
        unmasked_count = sum(1 for c in formatted if c.isalnum())
        chars_to_show = min(unmasked_count, 4)
        # Build result from end
        result = []
        shown = 0
        for char in reversed(formatted):
            if char.isalnum():
                shown += 1
                result.append(char if shown <= chars_to_show else "*")
            else:
                result.append(char)
        return "".join(reversed(result))

    def _mask_first4(self, formatted):
        """Mask all but first 4 alphanumeric characters."""
        if len(formatted) <= 4:
            return formatted
        result = []
        shown = 0
        for char in formatted:
            if char.isalnum():
                shown += 1
                result.append(char if shown <= 4 else "*")
            else:
                result.append(char)
        return "".join(result)

    def _mask_value(self, value):
        """Apply masking to a value (with formatting preserved)."""
        if value is None:
            return None

        str_value = str(value)
        if not str_value:
            return str_value

        # Apply formatting first so mask preserves the format
        formatted = self._format_value(str_value)

        if callable(self.mask):
            return self.mask(formatted)

        if self.mask == "last4":
            return self._mask_last4(formatted)

        if self.mask == "first4":
            return self._mask_first4(formatted)

        # Default: full mask (but preserve format characters)
        return "".join("*" if c.isalnum() else c for c in formatted)

    def _log_access(self, env, record_id, field_name, model_name, action="decrypt"):
        """Log access to encrypted field if audit is enabled."""
        if not self.audit:
            return
        try:
            env["pb.encrypted.audit.log"].sudo().create(
                {
                    "user_id": env.uid,
                    "model_name": model_name,
                    "field_name": field_name,
                    "record_id": record_id,
                    "action": action,
                }
            )
        except Exception as e:
            _logger.warning("Failed to log encrypted field access: %s", e)

    def convert_to_column(self, value, record, values=None, validate=True):
        """Convert Python value to database value (encrypt)."""
        if value is None or value is False:
            return None

        # Convert to string if needed
        if not isinstance(value, str):
            value = str(value)

        # Strip formatting before storage (store raw digits)
        value = self._strip_format(value)

        # Encrypt
        return encrypt_value(value)

    def convert_to_cache(self, value, record, validate=True):
        """Convert database value to cache value (decrypt)."""
        if value is None or value is False:
            return None

        # If it's not a string, assume it's already decrypted (e.g., from write)
        if not isinstance(value, str):
            return value

        # Check if it looks like encrypted data
        if is_encrypted_value(value):
            try:
                return decrypt_value(value)
            except Exception as e:
                _logger.error("Failed to decrypt field %s: %s", self.name, e)
                return None

        # Raw value (not encrypted), return as-is
        return value

    def convert_to_record(self, value, record):
        """Convert cache value to record value (always masked)."""
        if value is None:
            return None

        # Decrypt if needed
        if is_encrypted_value(value):
            try:
                value = decrypt_value(value)
            except Exception:
                return None

        # Always return masked value for display
        # Users must use get_unmasked_value() to see the real value
        return self._mask_value(value)

    def convert_to_read(self, value, record, use_display_name=True):
        """Convert cache value for read() method."""
        return self.convert_to_record(value, record)

    def convert_to_write(self, value, record):
        """Convert value for write operations."""
        if value is None or value is False:
            return None
        return value

    def convert_to_export(self, value, record):
        """Convert value for export (CSV, etc.)."""
        if value is None:
            return ""

        # Decrypt if needed
        if is_encrypted_value(value):
            try:
                value = decrypt_value(value)
            except Exception:
                return ""

        # Log export access
        if value and record:
            try:
                self._log_access(
                    record.env, record.id, self.name, record._name, action="export"
                )
            except Exception as e:
                # Don't fail export if audit logging fails
                _logger.warning("Failed to log export access: %s", e)

        # Always export masked value - prevents data leakage via export
        return self._mask_value(value)

    def convert_to_display_name(self, value, record):
        """Convert value for display_name."""
        return self.convert_to_record(value, record)

    def __get__(self, record, owner):
        """Override to handle decryption and access control on attribute access."""
        if record is None:
            return self

        value = super().__get__(record, owner)

        # If we got an encrypted value, decrypt it
        if is_encrypted_value(value):
            try:
                value = decrypt_value(value)
            except Exception:
                value = None

        # Always return masked value for display
        # Users with access can use get_unmasked_value() to see the real value
        if value is not None:
            return self._mask_value(value)

        return value

    # Block search operations
    def determine_domain(self, record, operator, value):
        """Block search operations on encrypted fields."""
        raise UserError(
            _(
                "Search operations are not allowed on encrypted field '%s'. "
                "Encrypted fields cannot be used in filters or search domains."
            )
            % self.name
        )


# Patch fields module to include Encrypted
fields.Encrypted = Encrypted
