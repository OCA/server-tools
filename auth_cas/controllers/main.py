# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
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
from openerp import SUPERUSER_ID
from openerp import http
from openerp.http import request
from openerp.addons.web.controllers.main import (
    Home, ensure_db, set_cookie_and_redirect, login_and_redirect
)
from openerp.tools.translate import _
from openerp.modules.registry import RegistryManager
import openerp
import logging
import functools
import werkzeug
import simplejson

_logger = logging.getLogger(__name__)


#----------------------------------------------------------
# helpers
#----------------------------------------------------------
def fragment_to_query_string(func):
    @functools.wraps(func)
    def wrapper(self, *a, **kw):
        kw.pop('debug', False)
        if not kw:
            return """<html><head><script>
                var l = window.location;
                var q = l.hash.substring(1);
                var r = l.pathname + l.search;
                if(q.length !== 0) {
                    var s = l.search ? (l.search === '?' ? '' : '&') : '?';
                    r = l.pathname + l.search + s + q;
                }
                if (r == l.pathname) {
                    r = '/';
                }
                window.location = r;
            </script></head><body></body></html>"""
        return func(self, *a, **kw)
    return wrapper


class CASLogin(Home):
    def list_cas_servers(self):
        ir_config_parameter_obj = request.registry.get('ir.config_parameter')
        cas_servers = ir_config_parameter_obj.search_read(
            request.cr, SUPERUSER_ID, [('key', '=', 'auth_cas.url_login')])

        service = ir_config_parameter_obj.search_read(
            request.cr, SUPERUSER_ID, [('key', '=', 'auth_cas.url_service')])
        if service:
            service = service[0]['value']
        else:
            service = ir_config_parameter_obj.search_read(
                request.cr, SUPERUSER_ID,
                [('key', '=', 'web.base.url')])[0]['value']

        state = self.get_state()
        res = []
        for cas in cas_servers:
            params = dict(
                service=service,
                debug=request.debug,
                state=simplejson.dumps(state)
            )
            res.append({
                'auth_link': cas['value'] + '?' + werkzeug.url_encode(params),
                'body': _('Log in with CAS'),
                'css_class': 'zsocial openerp'
            })

        return res

    def get_state(self):
        redirect = request.params.get('redirect') or 'web'
        if not redirect.startswith(('//', 'http://', 'https://')):
            redirect = '%s%s' % (
                request.httprequest.url_root,
                redirect[1:] if redirect[0] == '/' else redirect
            )
        state = dict(
            d=request.session.db,
            r=werkzeug.url_quote_plus(redirect),
        )
        ticket = request.params.get('ticket')
        if ticket:
            state['t'] = ticket
        return state

    @http.route()
    def web_login(self, *args, **kw):
        ensure_db()
        if request.httprequest.method == 'GET' and request.session.uid and \
           request.params.get('redirect'):
            # Redirect if already logged in and redirect param is present
            return http.redirect_with_hash(request.params.get('redirect'))
        elif request.params.get('redirect', False):
            ir_config_parameter_obj = request.registry.get(
                'ir.config_parameter')

            try:
                ticket = request.params.get('redirect')[
                    request.params.get('redirect').index('?')+1:]
                ticket = werkzeug.url_decode(ticket)
                ticket = ticket.get('ticket', False)
            except ValueError:
                ticket = False

            if ticket:
                login_url = ir_config_parameter_obj.search_read(
                    request.cr, SUPERUSER_ID,
                    [('key', '=', 'web.base.url')])[0]['value']
                return http.redirect_with_hash(
                    login_url + '/auth_cas/signin?db=%s&ticket=%s' % (
                        request.session.db, ticket))
            else:
                direct_login = ir_config_parameter_obj.search_read(
                    request.cr, SUPERUSER_ID,
                    [('key', '=', 'auth_cas.direct_login')])
                direct_login = (
                    direct_login and direct_login[0]['value'] or False
                )
                # If direct login is on and there's no casoff parameter on the
                # url, try to redirect to cas login url
                if direct_login and not (
                        request.params.get('casoff', False) or
                        request.params.get('login', False)):
                    return http.redirect_with_hash(
                        ir_config_parameter_obj.search_read(
                            request.cr, SUPERUSER_ID,
                            [('key', '=', 'auth_cas.url_login')])[0]['value'] +
                        '?service=' +
                        ir_config_parameter_obj.search_read(
                            request.cr, SUPERUSER_ID,
                            [('key', '=', 'auth_cas.url_service')])[0]['value']
                    )

        cas_servers = self.list_cas_servers()

        response = super(CASLogin, self).web_login(*args, **kw)
        if response.is_qweb:
            error = request.params.get('cas_error')
            if error == '2':
                error = _("Access Denied")
            elif error == '3':
                error = _(
                    "You do not have access to this database or your "
                    "invitation has expired. Please ask for an invitation "
                    "and be sure to follow the link in your invitation email."
                )
            else:
                error = None

            response.qcontext['cas_servers'] = cas_servers
            if error:
                response.qcontext['error'] = error

        return response

    @http.route()
    def web_auth_signup(self, *args, **kw):
        providers = self.list_providers()
        if len(providers) == 1:
            werkzeug.exceptions.abort(werkzeug.utils.redirect(
                providers[0]['auth_link'], 303))
        response = super(CASLogin, self).web_auth_signup(*args, **kw)
        response.qcontext.update(providers=providers)
        return response

    @http.route()
    def web_auth_reset_password(self, *args, **kw):
        providers = self.list_providers()
        if len(providers) == 1:
            werkzeug.exceptions.abort(
                werkzeug.utils.redirect(providers[0]['auth_link'], 303))
        response = super(CASLogin, self).web_auth_reset_password(*args, **kw)
        response.qcontext.update(providers=providers)
        return response


class CASController(http.Controller):

    @http.route('/auth_cas/signin', type='http', auth='none')
    @fragment_to_query_string
    def signin(self, **kw):
        state = simplejson.loads(kw.get('state', '{}'))
        dbname = request.session.db
        context = request.session.context
        registry = RegistryManager.get(dbname)
        with registry.cursor() as cr:
            try:
                u = registry.get('res.users')
                credentials = u.auth_cas(cr, SUPERUSER_ID, kw, context=context)
                cr.commit()
                action = state.get('a')
                menu = state.get('m')
                redirect = werkzeug.url_unquote_plus(state['r']) if state.get(
                    'r') else False
                url = '/web'
                if redirect:
                    url = redirect
                elif action:
                    url = '/web#action=%s' % action
                elif menu:
                    url = '/web#menu_id=%s' % menu
                return login_and_redirect(*credentials, redirect_url=url)
            except openerp.exceptions.AccessDenied:
                # cas credentials not valid, user could be on a temporary
                # session
                _logger.info(
                    'CAS: access denied, redirect to main page in case a '
                    'valid session exists, without setting cookies'
                )
                url = "/web/login?cas_error=3"
                redirect = werkzeug.utils.redirect(url, 303)
                redirect.autocorrect_location_header = False
                return redirect
            except Exception as e:
                # signup error
                _logger.exception("CAS: %s" % unicode(e))
                url = "/web/login?cas_error=2"

        return set_cookie_and_redirect(url)

    @http.route('/auth_cas/signout', type='http')
    def signout(self, **kw):
        redirect = '/web'
        if not request.params.get('casoff', False):
            ir_config_parameter_obj = request.registry.get(
                'ir.config_parameter')

            redirect = ir_config_parameter_obj.search_read(
                request.cr, SUPERUSER_ID,
                [('key', '=', 'auth_cas.url_logout')])[0]['value']

        request.session.logout(keep_db=True)
        return werkzeug.utils.redirect(redirect, 303)
