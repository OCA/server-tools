# -*- coding: utf-8 -*-
# Copyright (C):
#   * 2012-Today Serpent Consulting Services (<http://www.serpentcs.com>)
#   * 2016-Today GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import fields
from openerp.osv.orm import Model
from openerp.tools.translate import _


class MassSortConfig(Model):
    _name = 'mass.sort.config'

    # Column Section
    _columns = {
        'name': fields.char(
            string='Name', translate=True, required=True),
        'model_id': fields.many2one(
            'ir.model', string='Model', required=True),
        'allow_custom_setting': fields.boolean(
            string='Allow Custom Setting', help="If checked, any user could"
            " have the possibility to change fields, and use others."),
        'one2many_field_id': fields.many2one(
            'ir.model.fields', string='Field to Sort', required=True,
            domain="[('model_id', '=', model_id),"
            "('ttype', '=', 'one2many')]"),
        'one2many_model': fields.related(
            'one2many_field_id', 'relation', type='char',
            string='Model Name of the Field to Sort', readonly=True),
        'ref_ir_act_window': fields.many2one(
            'ir.actions.act_window', 'Sidebar Action', readonly=True),
        'ref_ir_value': fields.many2one(
            'ir.values', 'Sidebar Button', readonly=True),
        'line_ids': fields.one2many(
            'mass.sort.config.line', 'config_id', 'Sorting Criterias'),
    }

    _defaults = {
        'allow_custom_setting': True,
    }

    # Constraint Section
    def _check_model_sequence(self, cr, uid, ids, context=None):
        field_obj = self.pool['ir.model.fields']
        for config in self.browse(cr, uid, ids, context=context):
            if len(field_obj.search(cr, uid, [
                    ('model', '=', config.one2many_field_id.relation),
                    ('name', '=', 'sequence')], context=context)) != 1:
                return False
        return True

    def _check_model_field(self, cr, uid, ids, context=None):
        for config in self.browse(cr, uid, ids, context=context):
            if config.model_id.id != config.one2many_field_id.model_id.id:
                return False
        return True

    def _check_line_ids(self, cr, uid, ids, context=None):
        for config in self.browse(cr, uid, ids, context=context):
            if not config.allow_custom_setting and len(config.line_ids) == 0:
                return False
        return True

    _constraints = [
        (_check_model_sequence, "The selected Field to Sort doesn't not have"
            " 'sequence' field defined.", ['one2many_field_id']),
        (_check_model_field, "The selected Field to Sort doesn't belong to the"
            " selected model.", ['model_id', 'one2many_field_id']),
        (_check_line_ids, "You have to define field(s) in 'Sorting Criterias'"
            " if you uncheck 'Allow Custom Setting'.",
            ['line_ids', 'allow_custom_setting']),
    ]

    # View Section
    def on_change_one2many_field_id(
            self, cr, uid, ids, one2many_field_id, context=None):
        field_obj = self.pool['ir.model.fields']
        if not one2many_field_id:
            return {'value': {'one2many_model': False}}
        field = field_obj.browse(cr, uid, one2many_field_id, context=context)
        return {'value': {'one2many_model': field.relation}}

    # Overload Section
    def unlink(self, cr, uid, ids, context=None):
        self.unlink_action(cr, uid, ids, context=context)
        return super(MassSortConfig, self).unlink(
            cr, uid, ids, context=context)

    def copy(self, cr, uid, id, value=None, context=None):
        value = value or {}
        config = self.browse(cr, uid, id, context=context)
        value.update({
            'name': _('%s (copy)') % config.name,
            'ref_ir_act_window': False,
            'ref_ir_value': False})
        return super(MassSortConfig, self).copy(
            cr, uid, id, value, context=context)

    # Custom Section
    def create_action(self, cr, uid, ids, context=None):
        vals = {}
        action_obj = self.pool['ir.actions.act_window']
        values_obj = self.pool['ir.values']
        for config in self.browse(cr, uid, ids, context=context):
            src_obj = config.model_id.model
            button_name = _('Mass Sort (%s)') % config.name
            vals['ref_ir_act_window'] = action_obj.create(cr, uid, {
                'name': button_name,
                'type': 'ir.actions.act_window',
                'res_model': 'mass.sort.wizard',
                'src_model': src_obj,
                'view_type': 'form',
                'context': "{'mass_sort_config_id' : %d}" % (config.id),
                'view_mode': 'form,tree',
                'target': 'new',
                'auto_refresh': 1,
            }, context)
            vals['ref_ir_value'] = values_obj.create(cr, uid, {
                'name': button_name,
                'model': src_obj,
                'key2': 'client_action_multi',
                'value': (
                    "ir.actions.act_window,%s" % vals['ref_ir_act_window']),
                'object': True,
            }, context)
        self.write(cr, uid, ids, {
            'ref_ir_act_window': vals.get('ref_ir_act_window', False),
            'ref_ir_value': vals.get('ref_ir_value', False),
        }, context)
        return True

    def unlink_action(self, cr, uid, ids, context=None):
        action_obj = self.pool['ir.actions.act_window']
        values_obj = self.pool['ir.values']
        for config in self.browse(cr, uid, ids, context=context):
            if config.ref_ir_act_window:
                action_obj.unlink(
                    cr, uid, config.ref_ir_act_window.id, context=context)
            if config.ref_ir_value:
                values_obj.unlink(
                    cr, uid, config.ref_ir_value.id, context=context)
        return True
