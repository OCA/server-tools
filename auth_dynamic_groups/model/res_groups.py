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
import logging
from openerp.osv.orm import Model
from openerp.osv import fields
from openerp.tools.safe_eval import safe_eval
from openerp import SUPERUSER_ID


class res_groups(Model):
    _inherit = 'res.groups'

    _columns = {
        'is_dynamic': fields.boolean('Dynamic'),
        'dynamic_group_condition': fields.text(
            'Condition', help='The condition to be met for a user to be a '
            'member of this group. It is evaluated as python code at login '
            'time, you get `user` passed as a browse record')
    }

    def eval_dynamic_group_condition(self, cr, uid, ids, context=None):
        result = True
        user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, uid,
                                                 context=context)
        for this in self.browse(cr, uid, ids, context=context):
            result &= bool(
                safe_eval(
                    this.dynamic_group_condition,
                    {
                        'user': user,
                        'any': any,
                        'all': all,
                        'filter': filter,
                    }))
        return result

    def _check_dynamic_group_condition(self, cr, uid, ids, context=None):
        try:
            for this in self.browse(cr, uid, ids, context=context):
                if this.is_dynamic:
                    this.eval_dynamic_group_condition()
        except (NameError, SyntaxError, TypeError) as e:
            logging.info(e)
            return False
        return True

    _constraints = [
        (_check_dynamic_group_condition,
         'The condition doesn\'t evaluate correctly!',
         ['dynamic_group_condition']),
    ]

    def action_evaluate(self, cr, uid, ids, context=None):
        user_obj = self.pool.get('res.users')
        for user in user_obj.browse(
                cr, uid,
                user_obj.search(cr, uid, [], context=context),
                context=context):
            user_obj.update_dynamic_groups(user.id, cr.dbname)
