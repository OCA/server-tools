# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Therp BV (<http://therp.nl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.models import Model
from openerp.modules.registry import RegistryManager
from openerp import SUPERUSER_ID


class res_users(Model):
    _inherit = 'res.users'

    def _login(self, db, login, password):
        uid = super(res_users, self)._login(db, login, password)

        if uid:
            self.update_dynamic_groups(uid, db)

        return uid

    def update_dynamic_groups(self, uid, db):
        cr = self.pool._db.cursor(serialized=True)
        user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, uid)
        groups_obj = self.pool.get('res.groups')
        user.write(
            {
                'groups_id': [
                    (4, dynamic_group.id)
                    if dynamic_group.eval_dynamic_group_condition(uid=uid)
                    else (3, dynamic_group.id)
                    for dynamic_group in groups_obj.browse(
                        cr, SUPERUSER_ID,
                        groups_obj.search(cr, SUPERUSER_ID,
                                          [('is_dynamic', '=', True)]))
                ],
            })
        cr.commit()
        cr.close()
