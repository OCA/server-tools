# -*- coding: utf-8 -*-

import functools
import logging

import simplejson
import werkzeug.utils

import openerp
from openerp import _
from openerp import http
from openerp.http import request
from openerp import SUPERUSER_ID
# import openerp.addons.web.http as oeweb
from openerp.addons.web.controllers.main import set_cookie_and_redirect
from openerp.addons.web.controllers.main import ensure_db
from openerp.addons.web.controllers.main import login_and_redirect

_logger = logging.getLogger(__name__)


# ----------------------------------------------------------
# helpers
# ----------------------------------------------------------


def fragment_to_query_string(func):
    @functools.wraps(func)
    def wrapper(self, req, **kw):
        if not kw:
            return """<html><head><script>
                var l = window.location;
                var q = l.hash.substring(1);
                var r = '/' + l.search;
                if(q.length !== 0) {
                    var s = l.search ? (l.search === '?' ? '' : '&') : '?';
                    r = l.pathname + l.search + s + q;
                }
                window.location = r;
            </script></head><body></body></html>"""
        return func(self, req, **kw)
    return wrapper


# ----------------------------------------------------------
# Controller
# ----------------------------------------------------------


class SAMLLogin(openerp.addons.web.controllers.main.Home):

    def list_providers(self):
        try:
            provider_obj = request.registry.get('auth.saml.provider')
            providers = provider_obj.search_read(
                request.cr, SUPERUSER_ID, [('enabled', '=', True)]
            )
        except Exception, e:
            _logger.exception("SAML2: %s" % str(e))
            providers = []

        return providers

    @http.route()
    def web_login(self, *args, **kw):
        ensure_db()
        if (
            request.httprequest.method == 'GET' and
            request.session.uid and
            request.params.get('redirect')
        ):

            # Redirect if already logged in and redirect param is present
            return http.redirect_with_hash(request.params.get('redirect'))

        providers = self.list_providers()

        response = super(SAMLLogin, self).web_login(*args, **kw)
        if response.is_qweb:
            error = request.params.get('saml_error')
            if error == '1':
                error = _("Sign up is not allowed on this database.")
            elif error == '2':
                error = _("Access Denied")
            elif error == '3':
                error = _(
                    "You do not have access to this database or your "
                    "invitation has expired. Please ask for an invitation "
                    "and be sure to follow the link in your invitation email."
                )
            else:
                error = None

            response.qcontext['providers'] = providers

            if error:
                response.qcontext['error'] = error

        return response


class AuthSAMLController(http.Controller):

    def get_state(self, provider_id):
        """Compute a state to be sent to the IDP so it can forward it back to
        us.

        :rtype: Dictionary.
        """

        redirect = request.params.get('redirect') or 'web'
        if not redirect.startswith(('//', 'http://', 'https://')):
            redirect = '%s%s' % (
                request.httprequest.url_root,
                redirect[1:] if redirect[0] == '/' else redirect
            )

        state = {
            "d": request.session.db,
            "p": provider_id,
            "r": werkzeug.url_quote_plus(redirect),
        }
        return state

    @http.route('/auth_saml/get_auth_request', type='http', auth='none')
    def get_auth_request(self, pid):
        """state is the JSONified state object and we need to pass
        it inside our request as the RelayState argument
        """

        provider_id = int(pid)
        provider_osv = request.registry.get('auth.saml.provider')

        auth_request = None

        # store a RelayState on the request to our IDP so that the IDP
        # can send us back this info alongside the obtained token
        state = self.get_state(provider_id)

        try:
            auth_request = provider_osv._get_auth_request(
                request.cr, SUPERUSER_ID, provider_id, state
            )

        except Exception, e:
            _logger.exception("SAML2: %s" % str(e))

        # TODO: handle case when auth_request comes back as None

        redirect = werkzeug.utils.redirect(auth_request, 303)
        redirect.autocorrect_location_header = True
        return redirect

    @http.route('/auth_saml/signin', type='http', auth='none')
    @fragment_to_query_string
    def signin(self, req, **kw):
        """client obtained a saml token and passed it back
        to us... we need to validate it
        """
        saml_response = kw.get('SAMLResponse', None)

        if kw.get('RelayState', None) is None:
            # here we are in front of a client that went through
            # some routes that "lost" its relaystate... this can happen
            # if the client visited his IDP and successfully logged in
            # then the IDP gave him a portal with his available applications
            # but the provided link does not include the necessary relaystate
            url = "/?type=signup"
            redirect = werkzeug.utils.redirect(url, 303)
            redirect.autocorrect_location_header = True
            return redirect

        state = simplejson.loads(kw['RelayState'])
        provider = state['p']

        with request.registry.cursor() as cr:
            try:
                u = request.registry.get('res.users')
                credentials = u.auth_saml(
                    cr, SUPERUSER_ID, provider, saml_response
                )
                cr.commit()
                action = state.get('a')
                menu = state.get('m')
                url = '/'
                if action:
                    url = '/#action=%s' % action
                elif menu:
                    url = '/#menu_id=%s' % menu

                return login_and_redirect(*credentials, redirect_url=url)

            except AttributeError, e:
                # auth_signup is not installed
                _logger.error("auth_signup not installed on database "
                              "saml sign up cancelled.")
                url = "/#action=login&saml_error=1"

            except openerp.exceptions.AccessDenied:
                # saml credentials not valid,
                # user could be on a temporary session
                _logger.info('SAML2: access denied, redirect to main page '
                             'in case a valid session exists, '
                             'without setting cookies')

                url = "/#action=login&saml_error=3"
                redirect = werkzeug.utils.redirect(url, 303)
                redirect.autocorrect_location_header = False
                return redirect

            except Exception, e:
                # signup error
                _logger.exception("SAML2: %s" % str(e))
                url = "/#action=login&saml_error=2"

        return set_cookie_and_redirect(url)

# vim:expandtab:tabstop=4:softtabstop=4:shiftwidth=4:
