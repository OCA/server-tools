# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# DON'T IMPORT THIS MODULE IN __init__.py TO AVOID THE CREATION OF THE MODELS
# DEFINED FOR TESTS INTO YOUR ODOO INSTANCE

from odoo import fields, models
from odoo.fields import Domain


class RestrictFieldAccessPartner(models.Model):
    """Test model inheriting from the mixin and res.partner.
    Restricts access to all fields when test_credit_limit >= 42
    and the current user is not an admin."""

    _name = "res.partner"
    _inherit = ["res.partner", "restrict.field.access.mixin"]

    test_credit_limit = fields.Float(groups="base.group_user")

    def _restrict_field_access_is_field_accessible(self, field_name, action="read"):
        result = super()._restrict_field_access_is_field_accessible(
            field_name, action=action
        )
        if (
            not self._restrict_field_access_get_is_suspended()
            and not self.env.user.has_group("base.group_system")
            and field_name not in models.MAGIC_COLUMNS
            and self
        ):
            result = all(rec.sudo().test_credit_limit < 42 for rec in self)
        return result

    def _restrict_field_access_inject_restrict_field_access_domain(self, domain):
        return Domain.AND([domain, [("test_credit_limit", "<", 42)]])
