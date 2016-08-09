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
from openerp.osv.orm import Model
from openerp import pooler, SUPERUSER_ID


class res_users(Model):
    _inherit = 'res.users'

    def login(self, db, login, password):
        uid = super(res_users, self).login(db, login, password)

        if uid:
            self.update_dynamic_groups(uid, db)

        return uid

    def update_dynamic_groups(self, uid, db):
        cr = pooler.get_db(db).cursor()
        pool = pooler.get_pool(db)
        user = pool.get('res.users').browse(cr, SUPERUSER_ID, uid)
        groups_obj = pool.get('res.groups')
        user.write(
            {
                'groups_id': [
                    (4, dynamic_group.id)
                    if dynamic_group.eval_dynamic_group_condition()
                    else (3, dynamic_group.id)
                    for dynamic_group in groups_obj.browse(
                        cr, uid,
                        groups_obj.search(cr, uid,
                                          [('is_dynamic', '=', True)]))
                ],
            })
        cr.commit()
        cr.close()
