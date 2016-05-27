# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C):
#        2012-Today Serpent Consulting Services (<http://www.serpentcs.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from openerp.exceptions import UserError
from openerp import api, fields, models, _


class MassObject(models.Model):
    _name = "mass.object"

    name = fields.Char('Name', required=True, select=1)
    model_id = fields.Many2one('ir.model', 'Model', required=True,
                               help="Model is used for Selecting Fields."
                               "This is editable until Sidebar menu is not "
                               "created.")
    field_ids = fields.Many2many('ir.model.fields', 'mass_field_rel',
                                 'mass_id', 'field_id', 'Fields')
    ref_ir_act_window = fields.Many2one('ir.actions.act_window',
                                        'Sidebar action',
                                        readonly=True,
                                        help="Sidebar action to make this "
                                        "template available on records of "
                                        "the related document model.")
    ref_ir_value = fields.Many2one('ir.values', 'Sidebar button',
                                   readonly=True,
                                   help="Sidebar button to open"
                                   "the sidebar action")
    model_list = fields.Char('Model List')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', _('Name must be unique!')),
    ]

    @api.onchange('model_id')
    def onchange_model(self):
        self.field_ids = [(6, 0, [])]
        model_list = []
        if self.model_id:
            model_obj = self.env['ir.model']
            model_list = [self.model_id.id]
            active_model_obj = self.env[self.model_id.model]
            if active_model_obj._inherits:
                keys = active_model_obj._inherits.keys()
                inherits_model_list = model_obj.search([('model', 'in', keys)])
                model_list.extend((inherits_model_list and
                                   inherits_model_list.ids or []))
        self.model_list = model_list

    @api.multi
    def create_action(self):
        vals = {}
        action_obj = self.env['ir.actions.act_window']
        src_obj = self.model_id.model
        button_name = _('Mass Editing (%s)') % self.name
        vals['ref_ir_act_window'] = action_obj.create({
            'name': button_name,
            'type': 'ir.actions.act_window',
            'res_model': 'mass.editing.wizard',
            'src_model': src_obj,
            'view_type': 'form',
            'context': "{'mass_editing_object' : %d}" % (self.id),
            'view_mode': 'form, tree',
            'target': 'new',
            'auto_refresh': 1,
        }).id
        vals['ref_ir_value'] = self.env['ir.values'].create({
            'name': button_name,
            'model': src_obj,
            'key2': 'client_action_multi',
            'value': "ir.actions.act_window," + str(vals['ref_ir_act_window']),
            'object': True,
        }).id
        self.write(vals)
        return True

    @api.multi
    def unlink_action(self):
        for mass in self:
            try:
                if mass.ref_ir_act_window:
                    mass.ref_ir_act_window.unlink()
                if mass.ref_ir_value:
                    mass.ref_ir_value.unlink()
            except:
                raise UserError(_("Deletion of the action record failed."))
        return True

    @api.multi
    def unlink(self):
        self.unlink_action()
        return super(MassObject, self).unlink()

    @api.one
    def copy(self, default):
        if default is None:
            default = {}
        default.update({'name': _("%s (copy)" % self.name), 'field_ids': []})
        return super(MassObject, self).copy(default)


class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'

    @api.multi
    def module_uninstall(self):
        # search window actions of mass editing  and delete it
        if self.name == 'mass_editing':
            values_obj = self.env['ir.values']
            actions = self.env['ir.actions.act_window'].\
                search([('res_model', '=', 'mass.editing.wizard')])
            for action in actions:
                values_obj.\
                    search([('value', '=',
                             'ir.actions.act_window,%s' % action.id)]).unlink()
            actions.unlink()
        return super(IrModuleModule, self).module_uninstall()
