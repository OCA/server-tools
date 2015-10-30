# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Sergio Teruel
# (c) 2015 Antiun Ingeniería S.L. - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, api


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def _signup_create_user(self, values):
        account_type = values.get('account_type', False)
        if 'account_type' in values:
            values.pop('account_type')
        res = super(ResUsers, self)._signup_create_user(values)
        if isinstance(res, int):
            user = self.env['res.users'].browse(res)
            if account_type == 'supplier':
                user.partner_id.supplier = True
                user.groups_id = user.groups_id | self.env.ref(
                    'auth_supplier.group_auth_supplier')
        return res
