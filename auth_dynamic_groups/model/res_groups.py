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
from openerp import models, fields, api, exceptions
from openerp.tools.safe_eval import safe_eval
from openerp import _


class ResGroups(models.Model):
    _inherit = 'res.groups'

    is_dynamic = fields.Boolean('Dynamic')
    dynamic_group_condition = fields.Text(
        'Condition', help='The condition to be met for a user to be a '
        'member of this group. It is evaluated as python code at login '
        'time, you get `user` passed as a browse record')

    @api.multi
    def eval_dynamic_group_condition(self, uid=None):
        user = self.env['res.users'].browse([uid]) if uid else self.env.user
        result = all(
            self.mapped(
                lambda this: safe_eval(
                    this.dynamic_group_condition or 'False',
                    {
                        'user': user.sudo(),
                        'any': any,
                        'all': all,
                        'filter': filter,
                    })))
        return result

    @api.multi
    @api.constrains('dynamic_group_condition')
    def _check_dynamic_group_condition(self):
        try:
            self.filtered('is_dynamic').eval_dynamic_group_condition()
        except (NameError, SyntaxError, TypeError):
            raise exceptions.ValidationError(
                _('The condition doesn\'t evaluate correctly!'))

    @api.multi
    def action_evaluate(self):
        res_users = self.env['res.users']
        for user in res_users.search([]):
            res_users._model.update_dynamic_groups(user.id, self.env.cr.dbname)
