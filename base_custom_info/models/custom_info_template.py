# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Sergio Teruel
# (c) 2015 Antiun Ingeniería S.L. - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models, _


class CustomInfoTemplate(models.Model):
    _name = "custom.info.template"

    name = fields.Char()
    model_id = fields.Many2one(comodel_name='ir.model', string='Data Model')
    info_ids = fields.One2many(
        comodel_name='custom.info.template.line',
        inverse_name='template_id',
        string='Properties')


class CustomInfoTemplateLine(models.Model):
    _name = "custom.info.template.line"

    name = fields.Char()
    template_id = fields.Many2one(
        comodel_name='custom.info.template',
        string='Template')
    info_value_ids = fields.One2many(
        comodel_name="custom.info.value",
        inverse_name="custom_info_name_id",
        string="Property Values")


class CustomInfoValue(models.Model):
    _name = "custom.info.value"
    _rec_name = 'value'

    model = fields.Char(select=True)
    res_id = fields.Integer(select=True)
    custom_info_name_id = fields.Many2one(
        comodel_name='custom.info.template.line',
        string='Property Name')
    value = fields.Char()


class CustomInfo(models.AbstractModel):
    _name = "custom.info"

    custom_info_template_id = fields.Many2one(
        comodel_name='custom.info.template',
        string='Property Template')
    custom_info_ids = fields.One2many(
        comodel_name='custom.info.value',
        inverse_name='res_id',
        domain=lambda self: [('model', '=', self._name)],
        auto_join=True,
        string='Custom Properties')

    @api.onchange('custom_info_template_id')
    def _onchange_custom_info_template_id(self):
        if not self.custom_info_template_id:
            self.custom_info_ids = False
        else:
            info_list = self.custom_info_ids.mapped('custom_info_name_id')
            for info_name in self.custom_info_template_id.info_ids:
                if info_name not in info_list:
                    self.custom_info_ids |= self.custom_info_ids.new({
                        'model': self._name,
                        'custom_info_name_id': info_name.id,
                    })
