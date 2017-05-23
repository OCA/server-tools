# -*- coding: utf-8 -*-
# Copyright 2016 Serpent Consulting Services Pvt. Ltd. (support@serpentcs.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class MassObject(models.Model):
    _name = "mass.object"
    _description = "Mass Editing Object"

    name = fields.Char('Name', required=True, index=1)
    model_id = fields.Many2one('ir.model', 'Model', required=True,
                               help="Model is used for Selecting Fields. "
                                    "This is editable until Sidebar menu "
                                    "is not created.")
    field_ids = fields.Many2many('ir.model.fields', 'mass_field_rel',
                                 'mass_id', 'field_id', 'Fields')
    ref_ir_act_window_id = fields.Many2one('ir.actions.act_window',
                                           'Sidebar action',
                                           readonly=True,
                                           help="Sidebar action to make this "
                                                "template available on "
                                                "records of the related "
                                                "document model.")
    ref_ir_value_id = fields.Many2one('ir.values', 'Sidebar button',
                                      readonly=True,
                                      help="Sidebar button to open "
                                           "the sidebar action.")

    _sql_constraints = [
        ('name_uniq', 'unique (name)', _('Name must be unique!')),
    ]

    @api.multi
    def create_action(self):
        self.ensure_one()
        vals = {}
        action_obj = self.env['ir.actions.act_window']
        src_obj = self.model_id.model
        button_name = _('Mass Editing (%s)') % self.name
        vals['ref_ir_act_window_id'] = action_obj.create({
            'name': button_name,
            'type': 'ir.actions.act_window',
            'res_model': 'mass.editing.wizard',
            'src_model': src_obj,
            'view_type': 'form',
            'context': "{'mass_editing_object' : %d}" % (self.id),
            'view_mode': 'form,tree',
            'target': 'new',
        }).id
        # We make sudo as any user with rights in this model should be able
        # to create the action, not only admin
        vals['ref_ir_value_id'] = self.env['ir.values'].sudo().create({
            'name': button_name,
            'model': src_obj,
            'key2': 'client_action_multi',
            'value': "ir.actions.act_window," +
                     str(vals['ref_ir_act_window_id']),
        }).id
        self.write(vals)
        return True

    @api.multi
    def unlink_action(self):
        # We make sudo as any user with rights in this model should be able
        # to delete the action, not only admin
        self.mapped('ref_ir_act_window_id').sudo().unlink()
        self.mapped('ref_ir_value_id').sudo().unlink()
        return True

    @api.multi
    def unlink(self):
        self.unlink_action()
        return super(MassObject, self).unlink()

    @api.multi
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        if default is None:
            default = {}
        default.update({'name': _("%s (copy)" % self.name), 'field_ids': []})
        return super(MassObject, self).copy(default)
