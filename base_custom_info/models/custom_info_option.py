# -*- coding: utf-8 -*-
# Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# Copyright 2017 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import api, fields, models


class CustomInfoOption(models.Model):
    _description = "Available options for a custom property"
    _name = "custom.info.option"
    _order = "name"

    name = fields.Char(index=True, translate=True, required=True)
    property_ids = fields.Many2many(
        comodel_name="custom.info.property",
        string="Properties",
        help="Properties where this option is enabled.",
    )
    value_ids = fields.One2many(
        comodel_name="custom.info.value",
        inverse_name="value_id",
        string="Values",
        help="Values that have set this option.",
    )
    template_id = fields.Many2one(
        comodel_name="custom.info.template",
        string="Additional template",
        help="Additional template to be applied to the owner if this option "
             "is chosen.",
    )

    @api.multi
    def check_access_rule(self, operation):
        """You access an option if you access at least one property."""
        last = None
        for prop in self.mapped("property_ids"):
            try:
                prop.check_access_rule(operation)
                return
            except Exception as last:
                pass
        if last:
            raise last
        return super(CustomInfoOption, self).check_access_rule(operation)
