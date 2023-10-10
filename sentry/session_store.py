import logging

_logger = logging.getLogger(__name__)

try:
    from sentry_sdk.integrations.wsgi import SentryWsgiMiddleware
except ImportError:
    _logger.debug(
        "Cannot import 'sentry-sdk'.\
                        Please make sure it is installed."
    )


class CustomSentryWsgiMiddleware(SentryWsgiMiddleware):
    def __init__(self, application, session_store=None):
        super().__init__(application)
        self.session_store = session_store
