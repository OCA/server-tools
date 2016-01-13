# -*- coding: utf-8 -*-
# © 2015 Antiun Ingeniería S.L. - Sergio Teruel
# © 2015 Antiun Ingeniería S.L. - Carlos Dauden
# © 2015 Antiun Ingeniería S.L. - Jairo Llopis
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class CustomInfoTemplate(models.Model):
    """Defines custom properties expected for a given database object."""
    _name = "custom.info.template"
    _description = "Custom information template"
    _sql_constraints = [
        ("name_model",
         "UNIQUE (name, model_id)",
         "Another template with that name exists for that model."),
    ]

    name = fields.Char(translate=True)
    model_id = fields.Many2one(comodel_name='ir.model', string='Model')
    info_ids = fields.One2many(
        comodel_name='custom.info.property',
        inverse_name='template_id',
        string='Properties')


class CustomInfoProperty(models.Model):
    """Name of the custom information property."""
    _name = "custom.info.property"
    _description = "Custom information property"
    _sql_constraints = [
        ("name_template",
         "UNIQUE (name, template_id)",
         "Another property with that name exists for that template."),
    ]

    name = fields.Char(translate=True)
    template_id = fields.Many2one(
        comodel_name='custom.info.template',
        string='Template')
    info_value_ids = fields.One2many(
        comodel_name="custom.info.value",
        inverse_name="property_id",
        string="Property Values")


class CustomInfoValue(models.Model):
    _name = "custom.info.value"
    _description = "Custom information value"
    _rec_name = 'value'
    _sql_constraints = [
        ("property_model_res",
         "UNIQUE (property_id, model, res_id)",
         "Another property with that name exists for that resource."),
    ]

    model_id = fields.Many2one("ir.model", "Model", required=True)
    res_id = fields.Integer("Resource ID", index=True, required=True)
    property_id = fields.Many2one(
        comodel_name='custom.info.property',
        required=True,
        string='Property')
    name = fields.Char(related='property_id.name')
    value = fields.Char(translate=True)


class CustomInfo(models.AbstractModel):
    _name = "custom.info"
    _description = "Inheritable abstract model to add custom info in any model"

    custom_info_template_id = fields.Many2one(
        comodel_name='custom.info.template',
        string='Custom Information Template')
    custom_info_ids = fields.One2many(
        comodel_name='custom.info.value',
        inverse_name='res_id',
        domain=lambda self: [
            ("model_id", "=",
             self.env["ir.model"].search([("model", "=", self._name)]).id)],
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
                    })

    @api.multi
    def unlink(self):
        info_values = self.mapped('custom_info_ids')
        res = super(CustomInfo, self).unlink()
        if res:
            info_values.unlink()
        return res
