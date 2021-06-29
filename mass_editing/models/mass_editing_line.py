# -*- coding: utf-8 -*-
# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class MassEditingLine(models.Model):
    _name = "mass.editing.line"
    _order = "sequence,field_id"
    _description = "Mass Editing Line"

    sequence = fields.Integer()

    mass_editing_id = fields.Many2one(comodel_name="mass.editing")

    model_id = fields.Many2one(
        comodel_name="ir.model", related="mass_editing_id.model_id"
    )

    field_id = fields.Many2one(
        comodel_name="ir.model.fields",
        string="Field",
        domain="["
        "('name', '!=', '__last_update'),"
        "('ttype', 'not in', ['reference', 'function']),"
        "('model_id', '=', model_id)"
        "]",
    )

    widget_option = fields.Char(
        string="Widget Option",
        compute="_compute_widget_option",
        store=True,
        readonly=False,
        help="Add widget text that will be used"
        " to display the field in the wizard. Example :\n"
        "'many2many_tags', 'selection'",
    )
    apply_domain = fields.Boolean(
        default=False,
        string="Apply domain",
        help="Apply default domain related to field",
    )

    @api.depends("field_id")
    def _compute_widget_option(self):
        # this function propose selection, depending on the field
        for line in self.filtered("field_id"):
            field = line.field_id
            line.widget_option = False
            if field.ttype == "many2one":
                line.widget_option = "selection"
            elif field.ttype == "many2many":
                line.widget_option = "many2many_tags"
            elif field.ttype == "Binary":
                if "image" in field.name or "logo" in field.name:
                    line.widget_option = "image"
