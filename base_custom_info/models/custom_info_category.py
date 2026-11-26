# Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import fields, models

from .access import can_access_any_property, restrict_access


class CustomInfoCategory(models.Model):
    _description = "Categorize custom info properties"
    _name = "custom.info.category"
    _inherit = "custom.info.access.mixin"
    _order = "sequence, name"

    name = fields.Char(index=True, translate=True, required=True)
    sequence = fields.Integer(index=True)
    property_ids = fields.One2many(
        comodel_name="custom.info.property",
        inverse_name="category_id",
        string="Properties",
        help="Properties in this category.",
    )

    def _check_access(self, operation):
        return restrict_access(
            self, operation, super()._check_access(operation), can_access_any_property
        )
