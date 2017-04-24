# -*- coding: utf-8 -*-
# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class WizardModuleUninstall(models.TransientModel):
    _name = 'wizard.module.uninstall'

    def _default_module_id(self):
        return self._context.get('active_id', False)

    module_id = fields.Many2one(
        string='Module', comodel_name='ir.module.module', required=True,
        domain=[('state', 'not in', ['uninstalled', 'uninstallable'])],
        default=_default_module_id,
        help="Choose a module. The wizard will display all the models"
        " and fields linked to that module, that will be dropped,"
        " if selected module is uninstalled.\n"
        " Note : Only Non Transient items will be displayed")

    module_ids = fields.Many2many(
        string='Impacted modules', compute='_compute_module_ids',
        multi='module_ids',
        comodel_name='ir.module.module', readonly=True,
        help="Modules list that will be uninstalled by dependency")

    module_qty = fields.Integer(
        string='Impacted modules Quantity', compute='_compute_module_ids',
        multi='module_ids', readonly=True)

    module_name = fields.Char(
        string='Module Name', related='module_id.name', readonly=True)

    model_line_ids = fields.One2many(
        comodel_name='wizard.module.uninstall.line', readonly=True,
        inverse_name='wizard_id', domain=[('line_type', '=', 'model')])

    field_line_ids = fields.One2many(
        comodel_name='wizard.module.uninstall.line', readonly=True,
        inverse_name='wizard_id', domain=[('line_type', '=', 'field')])

    # Compute Section
    @api.multi
    @api.depends('module_id')
    def _compute_module_ids(self):
        for wizard in self:
            if wizard.module_id:
                res = wizard.module_id.downstream_dependencies()
                wizard.module_ids = res
                wizard.module_qty = len(res)
            else:
                wizard.module_ids = False
                wizard.module_qty = 0

    # OnChange Section
    @api.multi
    @api.onchange('module_id')
    def onchange_module_id(self):
        model_data_obj = self.env['ir.model.data']
        model_obj = self.env['ir.model']
        field_obj = self.env['ir.model.fields']

        for wizard in self:
            wizard.model_line_ids = False
            wizard.field_line_ids = False

        for wizard in self:
            model_ids = []
            module_names = wizard.module_ids.mapped('name')\
                + [wizard.module_id.name]
            # Get Models
            models_data = []
            all_model_ids = model_data_obj.search([
                ('module', 'in', module_names),
                ('model', '=', 'ir.model')]).mapped('res_id')
            all_model_ids = list(set(all_model_ids))
            for model in model_obj.browse(all_model_ids).filtered(
                    lambda x: not x.osv_memory):
                # Filter models that are not associated to other modules,
                # and that will be removed, if the selected module is
                # uninstalled
                other_declarations = model_data_obj.search([
                    ('module', 'not in', module_names),
                    ('model', '=', 'ir.model'),
                    ('res_id', '=', model.id)])
                if not len(other_declarations):
                    models_data.append((0, 0, {
                        'line_type': 'model',
                        'model_id': model.id,
                    }))
                    model_ids.append(model.id)
            wizard.model_line_ids = models_data

            # Get Fields
            fields_data = []
            all_field_ids = model_data_obj.search([
                ('module', 'in', module_names),
                ('model', '=', 'ir.model.fields')]).mapped('res_id')
            for field in field_obj.search([
                    ('id', 'in', all_field_ids),
                    ('model_id', 'not in', model_ids),
                    ('ttype', 'not in', ['one2many'])],
                    order='model_id, name'):
                other_declarations = model_data_obj.search([
                    ('module', 'not in', module_names),
                    ('model', '=', 'ir.model.field'),
                    ('res_id', '=', model.id)])
                if not len(other_declarations)\
                        and not field.model_id.osv_memory:
                    fields_data.append((0, 0, {
                        'line_type': 'field',
                        'field_id': field.id,
                    }))
            wizard.field_line_ids = fields_data
