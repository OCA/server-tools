# -*- coding: utf-8 -*-
from openerp import models, api, SUPERUSER_ID, _
from openerp.exceptions import ValidationError


class ChangeMaintenanceModeWizard(models.TransientModel):
    _name = 'change.maintenance.mode.wizard'

    @api.multi
    def select_maintenance_mode(self):
        ResUsers = self.env['res.users']
        context = self._context.copy()
        active_ids = context.get('active_ids', [])
        if len(active_ids) > 0:
            for user in ResUsers.browse(active_ids):
                if user.id == SUPERUSER_ID:
                    raise ValidationError(_("%s is superuser, so can not "
                                            "select maintenance mode.")
                                          % (user.name))
                user.write({'maintenance_mode': True, })
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def unselect_maintenance_mode(self):
        ResUsers = self.env['res.users']
        context = self._context.copy()
        active_ids = context.get('active_ids', [])
        if len(active_ids) > 0:
            for user in ResUsers.browse(active_ids):
                user.write({'maintenance_mode': False, })
        return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
