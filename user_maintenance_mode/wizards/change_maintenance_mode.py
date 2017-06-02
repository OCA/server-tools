# -*- coding: utf-8 -*-
from openerp import models, api, SUPERUSER_ID


class ChangeMaintenanceModeWizard(models.TransientModel):
    _name = 'change.maintenance.mode.wizard'

    @api.multi
    def select_maintenance_mode(self):
        ResUsers = self.env['res.users']
        Category = self.env['ir.module.category']
        Group = self.env['res.groups']
        context = self._context.copy()
        active_ids = context.get('active_ids', [])
        maintenance_category = Category.search([('name', '=',
                                                 'User Maintenance Mode')])
        user_ids = []
        for mc in maintenance_category:
            groups = Group.search([('category_id', '=', mc.id)])
            for group in groups:
                for user in group.users:
                    if user.id not in user_ids:
                        user_ids.append(user.id)
        if len(active_ids) > 0:
            for user in ResUsers.browse(active_ids):
                if user.id not in user_ids and user.id != SUPERUSER_ID:
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
