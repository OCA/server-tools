# -*- coding: utf-8 -*-
# © 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from openerp import _, api, fields, models
from openerp.exceptions import ValidationError


class CustomInfoTemplate(models.Model):
    """Defines custom properties expected for a given database object."""
    _description = "Custom information template"
    _name = "custom.info.template"
    _order = "model_id, name"
    _sql_constraints = [
        ("name_model",
         "UNIQUE (name, model)",
         "Another template with that name exists for that model."),
    ]

    name = fields.Char(required=True, translate=True)
    model = fields.Char(
        index=True,
        readonly=True,
        required=True)
    model_id = fields.Many2one(
        'ir.model',
        'Model',
        compute="_compute_model_id",
        store=True,
        ondelete="cascade",
    )
    property_ids = fields.One2many(
        'custom.info.property',
        'template_id',
        'Properties',
        oldname="info_ids",
        context={"embed": True},
    )

    @api.multi
    @api.depends("model")
    def _compute_model_id(self):
        """Get a related model from its name, for better UI."""
        for s in self:
            s.model_id = self.env["ir.model"].search([("model", "=", s.model)])

    @api.multi
    @api.constrains("model")
    def _check_model(self):
        """Ensure model exists."""
        for s in self:
            if s.model not in self.env:
                raise ValidationError(_("Model does not exist."))
            # Avoid error when updating base module and a submodule extends a
            # model that falls out of this one's dependency graph
            with self.env.norecompute():
                oldmodels = set(s.mapped("property_ids.info_value_ids.model"))
                if oldmodels and {s.model} != oldmodels:
                    raise ValidationError(
                        _("You cannot change the model because it is in use."))

    @api.multi
    def check_access_rule(self, operation):
        """You access a template if you access its model."""
        for s in self:
            model = self.env[s.model]
            model.check_access_rights(operation)
            model.check_access_rule(operation)
        return super(CustomInfoTemplate, self).check_access_rule(operation)
