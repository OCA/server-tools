import functools
import logging

import simplejson
import werkzeug.utils

import openerp
from openerp import SUPERUSER_ID
import openerp.addons.web.http as oeweb
from openerp.addons.web.controllers.main import set_cookie_and_redirect
from openerp.addons.web.controllers.main import login_and_redirect
from openerp.modules.registry import RegistryManager

_logger = logging.getLogger(__name__)

#----------------------------------------------------------
# helpers
#----------------------------------------------------------


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


#----------------------------------------------------------
# Controller
#----------------------------------------------------------
class SAMLController(oeweb.Controller):
    _cp_path = '/auth_saml'

    @oeweb.jsonrequest
    def list_providers(self, req, dbname):
        try:
            registry = RegistryManager.get(dbname)
            with registry.cursor() as cr:
                providers = registry.get('auth.saml.provider')
                l = providers.read(
                    cr, SUPERUSER_ID, providers.search(
                        cr, SUPERUSER_ID, [('enabled', '=', True)]
                    )
                )

        except Exception, e:
            _logger.exception("SAML2: %s" % str(e))
            l = []

        return l

    @oeweb.httprequest
    @fragment_to_query_string
    def signin(self, req, **kw):
        """JS client obtained a saml token and passed it back
        to us... we need to validate it
        """
        saml_response = kw.get('SAMLResponse', None)

        state = simplejson.loads(kw['RelayState'])
        dbname = state['d']
        provider = state['p']
        context = state.get('c', {})
        registry = RegistryManager.get(dbname)
        with registry.cursor() as cr:
            try:
                u = registry.get('res.users')
                credentials = u.auth_saml(
                    cr, SUPERUSER_ID, provider, saml_response, context=context
                )
                cr.commit()
                action = state.get('a')
                menu = state.get('m')
                url = '/'
                if action:
                    url = '/#action=%s' % action
                elif menu:
                    url = '/#menu_id=%s' % menu
                return login_and_redirect(req, *credentials, redirect_url=url)

            except AttributeError, e:
                print e
                # auth_signup is not installed
                _logger.error("auth_signup not installed on database %s: saml sign up cancelled." % (dbname,))
                url = "/#action=login&saml_error=1"

            except openerp.exceptions.AccessDenied:
                # saml credentials not valid,
                # user could be on a temporary session
                _logger.info('SAML2: access denied, redirect to main page in case a valid session exists, without setting cookies')
                url = "/#action=login&saml_error=3"
                redirect = werkzeug.utils.redirect(url, 303)
                redirect.autocorrect_location_header = False
                return redirect

            except Exception, e:
                # signup error
                _logger.exception("SAML2: %s" % str(e))
                url = "/#action=login&saml_error=2"

        return set_cookie_and_redirect(req, url)

# vim:expandtab:tabstop=4:softtabstop=4:shiftwidth=4:
