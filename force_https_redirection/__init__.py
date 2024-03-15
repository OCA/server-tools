# Copyright 2023 Foodles (http://www.foodles.co).
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import werkzeug
from odoo.service import wsgi_server


class RedirectMiddleware(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        """Redirect user to HTTPS in case of odoo is behind
        a reverse proxy and the connexion between client and
        reverse proxy was HTTP call.

        Popular reverse proxy set an header X-Forwarded-Proto
        that let the upstream server (odoo) knows what was the formal
        protocol used.

        In case of no proxy HTTP_X_FORWARDED_PROTO shouldn't be set
        so it won't redirect user to https.

        note: This middleware is called
        before werkzeug.middleware.proxy_fix.ProxyFix  middleware
        used when --proxy-mode is True
        """
        httprequest = werkzeug.wrappers.Request(environ)
        if httprequest.environ.get("HTTP_X_FORWARDED_PROTO") == "http":
            response = werkzeug.utils.redirect(
                httprequest.url.replace("http", "https", 1), 301
            )
            return response(environ, start_response)

        return self.app(environ, start_response)


wsgi_server.application = RedirectMiddleware(wsgi_server.application)
