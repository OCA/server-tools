# -*- coding: utf-8 -*-
# © 2016 Hans Henrik Gabelgaard www.steingabelgaard.dk
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import werkzeug
import operator
import logging
import openerp
from openerp import http
from openerp.http import request
from openerp.tools.translate import _
from openerp.exceptions import ValidationError, AccessDenied
from openerp.addons.web.controllers.main import Session
from openerp.addons.auth_signup.controllers.main import AuthSignupHome
from openerp.addons.auth_signup.res_users import SignupError


_logger = logging.getLogger(__name__)


class SessionEx(Session):

    @http.route('/web/session/change_password', type='json', auth="user")
    def change_password(self, fields):
        old_password, new_password, confirm_password = operator.itemgetter(
            'old_pwd', 'new_password', 'confirm_pwd')(dict(
                map(operator.itemgetter('name', 'value'), fields))
            )
        if not (old_password.strip() and new_password.strip() and
                confirm_password.strip()):
            return {
                'error': _('You cannot leave any password empty.'),
                'title': _('Change Password')
                }
        if new_password != confirm_password:
            return {
                'error': _('The new password and its confirmation must be'
                           ' identical.'),
                'title': _('Change Password')
                }
        try:
            if request.session.model('res.users').change_password(
                    old_password, new_password):
                return {'new_password': new_password}
        except AccessDenied:
            return {
                'error': _('The old password you provided is incorrect,'
                           ' your password was not changed.'),
                'title': _('Change Password')
                }
        return {
            'error': _('Error, password not changed !'),
            'title': _('Change Password')
            }


class AuthSignupHomeEx(AuthSignupHome):

    @http.route('/web/reset_password', type='http',
                auth='public', website=True)
    def web_auth_reset_password(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()

        if (not qcontext.get('token') and
                not qcontext.get('reset_password_enabled')):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                res_users = request.registry.get('res.users')
                if qcontext.get('token'):
                    res_users._validate_password(
                        request.cr, openerp.SUPERUSER_ID,
                        qcontext.get('password'),
                        raise_=True
                        )
                    self.do_signup(qcontext)
                    return super(AuthSignupHome, self).web_login(*args, **kw)
                else:
                    login = qcontext.get('login')
                    assert login, "No login provided."
                    res_users.reset_password(
                        request.cr, openerp.SUPERUSER_ID,
                        login
                        )
                    qcontext['message'] =\
                        _('An email has been sent with'
                          ' credentials to reset your password')
            except SignupError:
                qcontext['error'] = _("Could not reset your password")
                _logger.exception('error when resetting password')
            except ValidationError, e:
                qcontext['error'] = e.value
            except Exception, e:
                qcontext['error'] = _(e.message)

        return request.render('auth_signup.reset_password', qcontext)
