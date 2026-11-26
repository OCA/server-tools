# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models
from odoo.exceptions import AccessError


class CustomInfoAccessMixin(models.AbstractModel):
    _name = "custom.info.access.mixin"
    _description = "Access rules for custom information"

    def _fetch_query(self, query, fields):
        records = super()._fetch_query(query, fields)
        # SQL fetches apply ir.rules but do not call custom _check_access overrides.
        records.check_access("read")
        return records


def restrict_access(records, operation, base_result, can_access):
    """Combine the native rules with the permission on each related record."""
    candidates = records - base_result[0] if base_result else records
    denied = candidates.filtered(lambda record: not can_access(record, operation))
    if not denied:
        return base_result
    if base_result:
        return denied | base_result[0], base_result[1]
    return denied, lambda: AccessError(
        records.env._("You cannot access the related custom information.")
    )


def can_access_any_property(record, operation):
    properties = record.sudo().property_ids.with_env(record.env)
    return not properties or any(prop.has_access(operation) for prop in properties)
