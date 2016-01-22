# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Dhaval Patel
#    Copyright (C) 2011 - TODAY Denero Team. (<http://www.deneroteam.com>)
#                  2015 - TODAY Hans Henrik Gabelgaard
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

import string

from openerp import models, api
from openerp.tools.translate import _
from openerp.exceptions import ValidationError, AccessDenied

import operator
from openerp import http
from openerp.http import request
from openerp.addons.web.controllers.main import Session

class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def _validate_password(self, password, raise_=False):
        password_rules = []
        config_data = self.env[
            'base.config.settings'
        ].get_default_auth_password_settings()

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
        if problems and raise_:
            raise ValidationError(
                _("Password must match following rules\n-- %s ")
                % ("\n-- ".join(problems))
            )
        return problems

    @api.multi
    def write(self, values):
        if 'password' in values:
            self._validate_password(values['password'], raise_=True)
        return super(ResUsers, self).write(values)

    @api.one
    def _set_password(self, password):
        if password:
            self._validate_password(password, raise_=True)
        return super(ResUsers, self)._set_password(password)
    
class SessionEx(Session):
    
    @http.route('/web/session/change_password', type='json', auth="user")
    def change_password(self, fields):
        old_password, new_password,confirm_password = operator.itemgetter('old_pwd', 'new_password','confirm_pwd')(
                dict(map(operator.itemgetter('name', 'value'), fields)))
        if not (old_password.strip() and new_password.strip() and confirm_password.strip()):
            return {'error':_('You cannot leave any password empty.'),'title': _('Change Password')}
        if new_password != confirm_password:
            return {'error': _('The new password and its confirmation must be identical.'),'title': _('Change Password')}
        try:
            if request.session.model('res.users').change_password(
                old_password, new_password):
                return {'new_password':new_password}
        except AccessDenied:
            return {'error': _('The old password you provided is incorrect, your password was not changed.'), 'title': _('Change Password')}
        return {'error': _('Error, password not changed !'), 'title': _('Change Password')}
