from odoo import _, api, models
from odoo.exceptions import AccessError

from ..fields.encrypted import (
    Encrypted,
    apply_format,
    decrypt_value,
    is_encrypted_value,
)


class Base(models.AbstractModel):
    _inherit = "base"

    @api.model
    def _get_encrypted_fields(self):
        """Return list of encrypted field names on this model."""
        return [
            name for name, field in self._fields.items() if isinstance(field, Encrypted)
        ]

    def get_unmasked_value(self, field_name):
        """Get the unmasked (decrypted) value of an encrypted field.

        Only users with access to the field's encrypt_groups can call this.
        Access is logged to the audit log.

        Args:
            field_name: Name of the encrypted field

        Returns:
            dict: {record_id: unmasked_value} for each record in self

        Raises:
            AccessError: If user doesn't have access to the encrypted field
        """
        self.ensure_one()

        field = self._fields.get(field_name)
        if not field:
            raise ValueError(
                _("Field '%(field)s' does not exist on model '%(model)s'")
                % {"field": field_name, "model": self._name}
            )

        if not isinstance(field, Encrypted):
            raise ValueError(
                _("Field '%(field)s' is not an encrypted field") % {"field": field_name}
            )

        # Check access
        if not field._user_has_access(self.env):
            raise AccessError(
                _(
                    "You don't have access to view the unmasked value of "
                    "'%(field)s'. Required groups: %(groups)s"
                )
                % {"field": field_name, "groups": field.encrypt_groups or "None"}
            )

        # Log access
        field._log_access(self.env, self.id, field_name, self._name)

        # Get the raw value from cache (already decrypted by convert_to_cache)
        # We need to bypass __get__ which masks the value
        value = self.env.cache.get(self, field, None)

        # If not in cache, read from database and decrypt
        if value is None:
            self.env.cr.execute(
                f'SELECT "{field_name}" FROM "{self._table}" WHERE id = %(id)s',
                {"id": self.id},
            )
            row = self.env.cr.fetchone()
            if row and row[0]:
                db_value = row[0]
                if is_encrypted_value(db_value):
                    value = decrypt_value(db_value)
                else:
                    value = db_value

        # Apply formatting if configured
        if value and field.format_pattern:
            value = apply_format(value, field.format_pattern)

        return value
