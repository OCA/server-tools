# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Dhaval Patel
#    Copyright (C) 2011 - TODAY Denero Team. (<http://www.deneroteam.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import orm
from openerp.tools.safe_eval import safe_eval
from openerp.tools.translate import _
import string


class res_users(orm.Model):
    _inherit = "res.users"

    def _validate_password(self, cr, uid, password, context=None):
        icp = self.pool['ir.config_parameter']
        password_rules = []
        config_data = {
            'auth_password_min_character': safe_eval(
                icp.get_param(
                    cr,
                    uid,
                    'auth_password_settings.auth_password_min_character',
                    '6'
                )),
            'auth_password_has_capital_letter': safe_eval(
                icp.get_param(
                    cr,
                    uid,
                    'auth_password_settings.auth_password_has_capital_letter',
                    'False'
                )),
            'auth_password_has_digit': safe_eval(
                icp.get_param(
                    cr,
                    uid,
                    'auth_password_settings.auth_password_has_digit',
                    'False'
                )),
            'auth_password_has_special_letter': safe_eval(
                icp.get_param(
                    cr,
                    uid,
                    'auth_password_settings.auth_password_has_special_letter',
                    'False'
                )),
        }
        password_rules.append(
            lambda s:
                len(s) >= config_data.get('auth_password_min_character', 6) or
                _('Has %s or more characters') % (config_data.get(
                    'auth_password_min_character', 6)
                )
        )

        if (config_data.get('auth_password_has_capital_letter', False)):
            password_rules.append(
                lambda s: any(x.isupper() for x in s) or
                _('Has at least One Capital letter')
            )

        if (config_data.get('auth_password_has_digit', False)):
            password_rules.append(
                lambda s: any(x.isdigit() for x in s) or
                _('Has one Number')
            )

        if (config_data.get('auth_password_has_special_letter', False)):
            password_rules.append(
                lambda s: any(x in string.punctuation for x in s) or
                _('Has one Special letter')
            )
        problems = [
            p for p in [
                r(password) for r in password_rules
            ] if p and p is not True]
        return problems

    def write(self, cr, uid, ids, values, context=None):
        if 'password' in values:
            problems = self._validate_password(
                cr, uid, values['password'], context=context)
            if problems:
                raise orm.except_orm(
                    _('Error'),
                    _("Password must match following rules\n %s ")
                    % ("\n-- ".join(problems))
                )
        return super(res_users, self).write(cr, uid, ids, values, context)

    def _set_password(self, cr, uid, id, password, context=None):
        if password:
            problems = self._validate_password(
                cr, uid, password, context=context)
            if problems:
                raise orm.except_orm(
                    _('Error!'),
                    _("Password must match following rules\n %s ")
                    % ("\n-- ".join(problems))
                )
        return super(res_users, self)._set_password(
            cr, uid, id, password, context=context
        )
