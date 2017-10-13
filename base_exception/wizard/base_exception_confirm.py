# -*- coding: utf-8 -*-
# © 2011 Raphaël Valyi, Renato Lima, Guewen Baconnier, Sodexis
# © 2017 Akretion (http://www.akretion.com)
# Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ExceptionRuleConfirm(models.AbstractModel):

    _name = 'exception.rule.confirm'

    related_model_id = fields.Many2one('base.exception',)
    exception_ids = fields.Many2many('exception.rule',
                                     string='Exceptions to resolve',
                                     readonly=True)
    ignore = fields.Boolean('Ignore Exceptions')

    @api.model
    def default_get(self, field_list):
        res = super(ExceptionRuleConfirm, self).default_get(field_list)
        current_model = self._context.get('active_model')
        model_except_obj = self.env[current_model]
        active_ids = self._context.get('active_ids')
        assert len(active_ids) == 1, "Only 1 ID accepted, got %r" % active_ids
        active_id = active_ids[0]
        related_model_except = model_except_obj.browse(active_id)
        exception_ids = [e.id for e in related_model_except.exception_ids]
        res.update({'exception_ids': [(6, 0, exception_ids)]})
        res.update({'related_model_id': active_id})
        return res

    @api.multi
    def action_confirm(self):
        self.ensure_one()
        return {'type': 'ir.actions.act_window_close'}
