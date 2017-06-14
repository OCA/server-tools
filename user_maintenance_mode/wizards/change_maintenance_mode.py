# -*- coding: utf-8 -*-

from openerp import models, api, SUPERUSER_ID


class ChangeMaintenanceModeWizard(models.TransientModel):
    _name = 'change.maintenance.mode.wizard'

    @api.multi
    def _get_users(self, user_groups=None, type=None):
        # common
        context = self._context.copy()
        users = self.env['res.users'].browse(context.get('active_ids', []))
        if type == 'select':
            users = users.filtered(
                lambda user: user.id not in user_groups.mapped('id') and
                user.id != SUPERUSER_ID
            )
        return users

    @api.multi
    def select_maintenance_mode(self):
        Category = self.env['ir.module.category']
        Group = self.env['res.groups']
        maintenance_category = Category.search([('name', '=',
                                                 'User Maintenance Mode')])
        groups = Group.search([('category_id', 'in',
                                maintenance_category.mapped('id'))])
        user_groups = groups.mapped('users')
        users = self._get_users(user_groups=user_groups, type='select')
        users.write({'maintenance_mode': True, })
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def unselect_maintenance_mode(self):
        users = self._get_users(type='unselect')
        users.write({'maintenance_mode': False, })
        return {'type': 'ir.actions.act_window_close'}
