# -*- coding: utf-8 -*-
# © 2016 Serpent Consulting Services Pvt. Ltd. (support@serpentcs.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class MassObject(models.Model):
    _name = "mass.object"
    _description = "Mass Editing Object"

    name = fields.Char('Name', required=True, index=1)
    model_id = fields.Many2one('ir.model', 'Model', required=True,
                               ondelete="cascade",
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
    model_list = fields.Char('Model List')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', _('Name must be unique!')),
    ]

    @api.onchange('model_id')
    def _onchange_model_id(self):
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
        self.ensure_one()
        vals = {}
        action_obj = self.env['ir.actions.act_window']
        src_obj = self.model_id.model
        button_name = _('Mass Editing (%s)') % self.name
        self.ref_ir_act_window_id = action_obj.create({
                                                'name': button_name,
                                                'type': 'ir.actions.act_window',
                                                'res_model': 'mass.editing.wizard',
                                                'src_model': src_obj,
                                                'view_type': 'form',
                                                'binding_model_id': self.model_id.id,
                                                'binding_type': 'action',
                                                'context': "{'mass_editing_object' : %d}" % (self.id),
                                                'view_mode': 'form, tree',
                                                'target': 'new',
                                            }).id
        return True

    @api.multi
    def unlink_action(self):
        # We make sudo as any user with rights in this model should be able
        # to delete the action, not only admin
        self.mapped('ref_ir_act_window_id').sudo().unlink()
        return True

    @api.multi
    def unlink(self):
        self.unlink_action()
        return super(MassObject, self).unlink()

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        if default is None:
            default = {}
        default.update({'name': _("%s (copy)" % self.name), 'field_ids': []})
        return super(MassObject, self).copy(default)
