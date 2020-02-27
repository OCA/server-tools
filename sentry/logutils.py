# Copyright 2016-2017 Versada <https://versada.eu/>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import urllib.parse

import odoo.http

_logger = logging.getLogger(__name__)
try:
    from raven.handlers.logging import SentryHandler
    from raven.processors import SanitizePasswordsProcessor
    from raven.utils.wsgi import get_environ, get_headers
except ImportError:
    _logger.debug('Cannot import "raven". Please make sure it is installed.')
    SentryHandler = object
    SanitizePasswordsProcessor = object


def get_request_info(request):
    """
    Returns context data extracted from :param:`request`.

    Heavily based on flask integration for Sentry: https://git.io/vP4i9.
    """
    urlparts = urllib.parse.urlsplit(request.url)
    return {
        "url": "{}://{}{}".format(urlparts.scheme, urlparts.netloc, urlparts.path),
        "query_string": urlparts.query,
        "method": request.method,
        "headers": dict(get_headers(request.environ)),
        "env": dict(get_environ(request.environ)),
    }


def get_extra_context():
    """
    Extracts additional context from the current request (if such is set).
    """
    request = odoo.http.request
    try:
        session = getattr(request, "session", {})
    except RuntimeError:
        ctx = {}
    else:
        ctx = {
            "tags": {"database": session.get("db", None)},
            "user": {
                "login": session.get("login", None),
                "uid": session.get("uid", None),
            },
            "extra": {"context": session.get("context", {})},
        }
        if request.httprequest:
            ctx.update({"request": get_request_info(request.httprequest)})
    return ctx


class LoggerNameFilter(logging.Filter):
    """
    Custom :class:`logging.Filter` which allows to filter loggers by name.
    """

    def __init__(self, loggers, name=""):
        super(LoggerNameFilter, self).__init__(name=name)
        self._exclude_loggers = set(loggers)

    def filter(self, event):
        return event.name not in self._exclude_loggers


class OdooSentryHandler(SentryHandler):
    """
    Customized :class:`raven.handlers.logging.SentryHandler`.

    Allows to add additional Odoo and HTTP request data to the event which is
    sent to Sentry.
    """

    def __init__(self, include_extra_context, *args, **kwargs):
        super(OdooSentryHandler, self).__init__(*args, **kwargs)
        self.include_extra_context = include_extra_context

    def emit(self, record):
        if self.include_extra_context:
            self.client.context.merge(get_extra_context())
        return super(OdooSentryHandler, self).emit(record)


class SanitizeOdooCookiesProcessor(SanitizePasswordsProcessor):
    """
    Custom :class:`raven.processors.Processor`.

    Allows to sanitize sensitive Odoo cookies, namely the "session_id" cookie.
    """

    KEYS = FIELDS = frozenset(["session_id"])
