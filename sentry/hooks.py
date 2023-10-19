# Copyright 2016-2017 Versada <https://versada.eu/>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import warnings
from collections import abc
from decimal import Decimal

import odoo.http
from odoo.service.server import server
from odoo.tools import config as odoo_config

from . import const
from .logutils import (
    InvalidGitRepository,
    SanitizeOdooCookiesProcessor,
    fetch_git_sha,
    get_extra_context,
)

_logger = logging.getLogger(__name__)
TRACES_SAMPLER_OPTION = [
    "traces_sample_rate_http",
    "traces_sample_rate_cron",
    "traces_sample_rate_job",
]
HAS_SENTRY_SDK = True
try:
    import sentry_sdk
    from sentry_sdk.integrations.logging import ignore_logger
    from sentry_sdk.integrations.threading import ThreadingIntegration
    from sentry_sdk.integrations.wsgi import SentryWsgiMiddleware
except ImportError:  # pragma: no cover
    HAS_SENTRY_SDK = False  # pragma: no cover
    _logger.debug(
        "Cannot import 'sentry-sdk'.\
                        Please make sure it is installed."
    )  # pragma: no cover


def before_send(event, hint):
    """Prevent the capture of any exceptions in
    the DEFAULT_IGNORED_EXCEPTIONS list
        -- or --
    Add context to event if include_context is True
    and sanitize sensitive data"""

    exc_info = hint.get("exc_info")
    if exc_info is None and "log_record" in hint:
        # Odoo handles UserErrors by logging the raw exception rather
        # than a message string in odoo/http.py
        try:
            module_name = hint["log_record"].msg.__module__
            class_name = hint["log_record"].msg.__class__.__name__
            qualified_name = module_name + "." + class_name
        except AttributeError:
            qualified_name = "not found"

        if qualified_name in const.DEFAULT_IGNORED_EXCEPTIONS:
            return None

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
        _logger.debug("Odoo directory: '%s' not a valid git repository", odoo_dir)

class Sampler:
    def __init__(self, params):
        super().__init__()
        default_rate = params.pop("default_rate", 0)
        for key in TRACES_SAMPLER_OPTION:
            setattr(self, key, Decimal(params.get(key, default_rate)))

    def traces_sampler(self, sampling_context):
        path = sampling_context.get("wsgi_environ", {}).get("PATH_INFO")
        op = sampling_context.get("transaction_context", {}).get("op")
        if path and path.startswith("/longpolling"):
            return 0
        elif path and path.startswith("/queue_job"):
            return self.traces_sample_rate_job
        elif op == "cron":
            return self.traces_sample_rate_cron
        elif op == "http.server":
            return self.traces_sample_rate_http
        else:
            # This case should not happen
            _logger.warning("No sample rate define for context {}", sampling_context)
            return 0

def initialize_sentry(config):
    """Setup an instance of :class:`sentry_sdk.Client`.
    :param config: Sentry configuration
    :param client: class used to instantiate the sentry_sdk client.
    """
    enabled = config.get("sentry_enabled", False)
    if not (HAS_SENTRY_SDK and enabled):
        return
    _logger.info("Initializing sentry...")
    if config.get("sentry_odoo_dir") and config.get("sentry_release"):
        _logger.debug(
            "Both sentry_odoo_dir and \
                       sentry_release defined, choosing sentry_release"
        )
    if config.get("sentry_transport"):
        warnings.warn(
            "`sentry_transport` has been deprecated.  "
            "Its not neccesary send it, will use `HttpTranport` by default.",
            DeprecationWarning,
        )
    options = {}
    for option in const.get_sentry_options():
        value = config.get("sentry_%s" % option.key, option.default)
        if isinstance(option.converter, abc.Callable):
            value = option.converter(value)
        options[option.key] = value

    exclude_loggers = const.split_multiple(
        config.get("sentry_exclude_loggers", const.DEFAULT_EXCLUDE_LOGGERS)
    )

    if not options.get("release"):
        options["release"] = config.get(
            "sentry_release", get_odoo_commit(config.get("sentry_odoo_dir"))
        )

    # Change name `ignore_exceptions` (with raven)
    # to `ignore_errors' (sentry_sdk)
    options["ignore_errors"] = options["ignore_exceptions"]
    del options["ignore_exceptions"]

    options["before_send"] = before_send

    options["integrations"] = [
        const.get_sentry_logging(config),
        ThreadingIntegration(propagate_hub=True),
    ]
    # Remove logging_level, since in sentry_sdk is include in 'integrations'

    sampler_params = {
        key: config[f"sentry_{key}"]
        for key in TRACES_SAMPLER_OPTION
        if config.get(f"sentry_{key}") is not None
    }

    if options["traces_sample_rate"]:
        # use traces_sample_rate as default rate
        sampler_params["default_rate"] = options.pop("traces_sample_rate")

    if sampler_params:
        # We always use traces_sampler even if only the traces_sample_rate
        # have been define, because some transaction like longpolling
        # should be never send and the method traces_sampler can drop them
        options["traces_sampler"] = Sampler(sampler_params).traces_sampler

    client = sentry_sdk.init(**options)

    sentry_sdk.set_tag("include_context", config.get("sentry_include_context", True))

    if exclude_loggers:
        for item in exclude_loggers:
            ignore_logger(item)

    # The server app is already registered so patch it here
    if server:
        server.app = SentryWsgiMiddleware(server.app)

    # Patch the wsgi server in case of further registration
    odoo.http.Application = SentryWsgiMiddleware(odoo.http.Application)

    with sentry_sdk.push_scope() as scope:
        scope.set_extra("debug", False)
        sentry_sdk.capture_message("Starting Odoo Server", "info")

    return client


def post_load():
    initialize_sentry(odoo_config)
