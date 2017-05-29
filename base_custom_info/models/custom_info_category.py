# -*- coding: utf-8 -*-
# Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import api, fields, models


class CustomInfoCategory(models.Model):
    _description = "Categorize custom info properties"
    _name = "custom.info.category"
    _order = "sequence, name"

    name = fields.Char(index=True, translate=True, required=True)
    sequence = fields.Integer(index=True)
    property_ids = fields.One2many(
        comodel_name="custom.info.property",
        inverse_name="category_id",
        string="Properties",
        help="Properties in this category.",
    )

    @api.multi
    def check_access_rule(self, operation):
        """You access a category if you access at least one property."""
        last = None
        for prop in self.mapped("property_ids"):
            try:
                prop.check_access_rule(operation)
                return
            except Exception as last:
                pass
        if last:
            raise last
        return super(CustomInfoCategory, self).check_access_rule(operation)
