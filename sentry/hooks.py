# Copyright 2016-2017 Versada <https://versada.eu/>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

import odoo.http
from odoo.service import wsgi_server
from odoo.tools import config as odoo_config

from . import const
from .logutils import SanitizeOdooCookiesProcessor, fetch_git_sha
from .logutils import InvalidGitRepository, get_extra_context

import collections

_logger = logging.getLogger(__name__)
HAS_SENTRY_SDK = True
try:
    import sentry_sdk
    from sentry_sdk.integrations.wsgi import SentryWsgiMiddleware
    from sentry_sdk.integrations.threading import ThreadingIntegration
    from sentry_sdk.integrations.logging import ignore_logger
except ImportError:  # pragma: no cover
    HAS_SENTRY_SDK = False   # pragma: no cover
    _logger.debug("Cannot import 'sentry-sdk'.\
                        Please make sure it is installed.")   # pragma: no cover


def before_send(event, hint):
    """ Add context to event if include_context is True
        and sanitize sensitive data """
    if event.setdefault("tags", {})["include_context"]:
        cxtest = get_extra_context(odoo.http.request)
        info_request = ["tags", "user", "extra", "request"]

        for item in info_request:
            info_item = event.setdefault(item, {})
            info_item.update(cxtest.setdefault(item, {}))

    raven_processor = SanitizeOdooCookiesProcessor()
    raven_processor.process(event)

    return event


def get_odoo_commit(odoo_dir):
    """Attempts to get Odoo git commit from :param:`odoo_dir`."""
    if not odoo_dir:
        return
    try:
        return fetch_git_sha(odoo_dir)
    except InvalidGitRepository:
        _logger.debug(
            "Odoo directory: '%s' not a valid git repository", odoo_dir)


def initialize_sentry(config):
    """  Setup an instance of :class:`sentry_sdk.Client`.
        :param config: Sentry configuration
        :param client: class used to instantiate the sentry_sdk client.
    """
    enabled = config.get("sentry_enabled", False)
    if not (HAS_SENTRY_SDK and enabled):
        return
    _logger.info("Initializing sentry...")
    if config.get("sentry_odoo_dir") and config.get("sentry_release"):
        _logger.debug("Both sentry_odoo_dir and \
                       sentry_release defined, choosing sentry_release")
    options = {
        "release": config.get("sentry_release",
                              get_odoo_commit(config.get("sentry_odoo_dir"))),
    }
    for option in const.get_sentry_options():
        value = config.get('sentry_%s' % option.key, option.default)
        if isinstance(option.converter, collections.Callable):
            value = option.converter(value)
        options[option.key] = value

    exclude_loggers = const.split_multiple(
        config.get("sentry_exclude_loggers", const.DEFAULT_EXCLUDE_LOGGERS)
    )
    # Change name `ignore_exceptions` (with raven)
    # to `ignore_errors' (sentry_sdk)
    options["ignore_errors"] = options["ignore_exceptions"]
    del options["ignore_exceptions"]

    options["before_send"] = before_send

    options["integrations"] = [options["logging_level"],
                               ThreadingIntegration(propagate_hub=True)]
    # Remove logging_level, since in sentry_sdk is include in 'integrations'
    del options["logging_level"]

    client = sentry_sdk.init(**options)

    sentry_sdk.set_tag("include_context",
                       config.get("sentry_include_context", True))

    if exclude_loggers:
        for item in exclude_loggers:
            ignore_logger(item)

    wsgi_server.application = SentryWsgiMiddleware(wsgi_server.application)

    with sentry_sdk.push_scope() as scope:
        scope.set_extra("debug", False)
        sentry_sdk.capture_message("Starting Odoo Server", "info")

    return client


def post_load():
    initialize_sentry(odoo_config)
