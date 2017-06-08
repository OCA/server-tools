# -​*- coding: utf-8 -*​-
##############################################################################
#
#    Copyright 2009-2016 Trobz (<http://trobz.com>).
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
import operator

import openerp
from openerp import http
from openerp.http import request
from openerp.tools.translate import _
from openerp.addons.web.controllers.main import Session


class Session(Session):

    @http.route('/web/session/change_password', type='json', auth="user")
    def change_password(self, fields):
        '''
        Overwrite this function to allow to raise other types of error messages
        '''
        old_password, new_password, confirm_password = operator.itemgetter(
            'old_pwd', 'new_password', 'confirm_pwd')(
                dict(map(operator.itemgetter('name', 'value'), fields)))
        if not (old_password.strip() and new_password.strip() and
                confirm_password.strip()):
            return {'error': _('You cannot leave any password empty.'),
                    'title': _('Change Password')}
        if new_password != confirm_password:
            return {'title': _('Change Password'), 'error':
                    _('The new password and its confirmation '
                      'must be identical.')}
        try:
            if request.session.model('res.users').change_password(
                                                old_password, new_password):
                return {'new_password': new_password}
        # standard exception from Odoo
        except openerp.exceptions.AccessDenied:
            return {'error': _('The old password you provided is incorrect,'
                               ' your password was not changed.'),
                    'title': _('Change Password')}
        # other types of error messages
        except Exception, e:
            # raise other error message when changing password
            return {'error': e[0], 'title': _('Change Password')}
        return {'error': _('Error, password not changed !'),
                'title': _('Change Password')}
