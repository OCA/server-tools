# -*- coding: utf-8 -*-
# © 2015 Antiun Ingeniería S.L. - Sergio Teruel
# © 2015 Antiun Ingeniería S.L. - Carlos Dauden
# © 2015 Antiun Ingeniería S.L. - Jairo Llopis
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class CustomInfoModelLink(models.AbstractModel):
    _description = "A model that gets its ``ir.model`` computed"
    _name = "custom.info.model_link"

    model = fields.Char(
        index=True,
        readonly=True,
        required=True)
    model_id = fields.Many2one(
        'ir.model',
        'Model',
        compute="_compute_model_id",
        store=True)

    @api.multi
    @api.depends("model")
    def _compute_model_id(self):
        """Get a related model from its name, for better UI."""
        for s in self:
            s.model_id = self.env["ir.model"].search([("model", "=", s.model)])


class CustomInfoTemplate(models.Model):
    """Defines custom properties expected for a given database object."""
    _description = "Custom information template"
    _name = "custom.info.template"
    _inherit = "custom.info.model_link"
    _sql_constraints = [
        ("name_model",
         "UNIQUE (name, model)",
         "Another template with that name exists for that model."),
    ]

    name = fields.Char(required=True, translate=True)
    info_ids = fields.One2many(
        'custom.info.property',
        'template_id',
        'Properties')


class CustomInfoProperty(models.Model):
    """Name of the custom information property."""
    _description = "Custom information property"
    _name = "custom.info.property"
    _sql_constraints = [
        ("name_template",
         "UNIQUE (name, template_id)",
         "Another property with that name exists for that template."),
    ]

    name = fields.Char(required=True, translate=True)
    template_id = fields.Many2one(
        comodel_name='custom.info.template',
        string='Template',
        required=True)
    info_value_ids = fields.One2many(
        comodel_name="custom.info.value",
        inverse_name="property_id",
        string="Property Values")


class CustomInfoValue(models.Model):
    _description = "Custom information value"
    _name = "custom.info.value"
    _inherit = "custom.info.model_link"
    _rec_name = 'value'
    _sql_constraints = [
        ("property_model_res",
         "UNIQUE (property_id, model, res_id)",
         "Another property with that name exists for that resource."),
    ]

    res_id = fields.Integer("Resource ID", index=True, required=True)
    property_id = fields.Many2one(
        comodel_name='custom.info.property',
        required=True,
        string='Property')
    name = fields.Char(related='property_id.name', readonly=True)
    value = fields.Char(translate=True, index=True)


class CustomInfo(models.AbstractModel):
    _description = "Inheritable abstract model to add custom info in any model"
    _name = "custom.info"

    custom_info_template_id = fields.Many2one(
        comodel_name='custom.info.template',
        string='Custom Information Template')
    custom_info_ids = fields.One2many(
        comodel_name='custom.info.value',
        inverse_name='res_id',
        domain=lambda self: [("model", "=", self._name)],
        auto_join=True,
        string='Custom Properties')

    @api.multi
    @api.onchange('custom_info_template_id')
    def _onchange_custom_info_template_id(self):
        if not self.custom_info_template_id:
            self.custom_info_ids = False
        else:
            info_list = self.custom_info_ids.mapped('property_id')
            for info_name in self.custom_info_template_id.info_ids:
                if info_name not in info_list:
                    self.custom_info_ids |= self.custom_info_ids.new({
                        'model': self._name,
                        'property_id': info_name.id,
                        "res_id": self.id,
                    })

    @api.multi
    def unlink(self):
        info_values = self.mapped('custom_info_ids')
        res = super(CustomInfo, self).unlink()
        if res:
            info_values.unlink()
        return res
