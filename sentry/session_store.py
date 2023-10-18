import logging
from odoo import http

try:
    from sentry_sdk.integrations.wsgi import SentryWsgiMiddleware
except ImportError:
    _logger.debug(
        "Cannot import 'sentry-sdk'.\
                        Please make sure it is installed."
    )

_logger = logging.getLogger(__name__)

class CustomSentryWsgiMiddleware(SentryWsgiMiddleware):
    def __init__(self, application):
        super().__init__(application)

    def __call__(self, environ, start_response):
        if hasattr(http.Application, 'session_store'):
            session_store = http.Application.session_store
            _logger.info("SENTRY::session_store")
            _logger.info(session_store)
        else:
            _logger.warning("SENTRY:: redis session_store is not available on http.Application")
        return super().__call__(environ, start_response)
