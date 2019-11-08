# Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# Copyright 2017 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CustomInfoTemplate(models.Model):
    """Defines custom properties expected for a given database object."""
    _description = "Custom information template"
    _name = "custom.info.template"
    _order = "model_id, name"
    _sql_constraints = [
        ("name_model",
         "UNIQUE (name, model_id)",
         "Another template with that name exists for that model."),
    ]

    name = fields.Char(required=True, translate=True)
    model = fields.Char(
        string="Model technical name", inverse="_inverse_model",
        compute="_compute_model", search="_search_model"
    )
    model_id = fields.Many2one(
        comodel_name='ir.model', string='Model', ondelete="restrict",
        required=True, auto_join=True,
    )
    property_ids = fields.One2many(
        comodel_name='custom.info.property', inverse_name='template_id',
        string='Properties', oldname="info_ids",
    )

    @api.multi
    @api.depends("model_id")
    def _compute_model(self):
        for r in self:
            r.model = r.model_id.model

    @api.multi
    def _inverse_model(self):
        for r in self:
            r.model_id = self.env["ir.model"].search([("model", "=", r.model)])

    @api.model
    def _search_model(self, operator, value):
        models = self.env['ir.model'].search([('model', operator, value)])
        return [('model_id', 'in', models.ids)]

    @api.onchange('model')
    def _onchange_model(self):
        self._inverse_model()

    @api.multi
    def _check_model_update_allowed(self, model_id):
        """Check if the template's model can be updated.

        Template can be updated only if no property values already exists for
        this template
        """
        for record in self:
            if (model_id != record.model_id.id
                    and record.mapped("property_ids.info_value_ids")):
                raise ValidationError(
                    _("You cannot change the model because it is in use.")
                )

    @api.multi
    def check_access_rule(self, operation):
        """You access a template if you access its model."""
        for record in self:
            model = self.env[record.model_id.model or record.model]
            model.check_access_rights(operation)
            model.check_access_rule(operation)
        return super().check_access_rule(operation)

    @api.multi
    def write(self, vals):
        if 'model_id' in vals:
            self._check_model_update_allowed(vals['model_id'])
        return super().write(vals)
