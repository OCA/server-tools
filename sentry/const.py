# Copyright 2016-2017 Versada <https://versada.eu/>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import collections
import logging

from sentry_sdk.consts import DEFAULT_OPTIONS
from sentry_sdk.integrations.logging import LoggingIntegration

import odoo.loglevels


def split_multiple(string, delimiter=",", strip_chars=None):
    """Splits :param:`string` and strips :param:`strip_chars` from values."""
    if not string:
        return []
    return [v.strip(strip_chars) for v in string.split(delimiter)]


def to_int_if_defined(value):
    if value == "" or value is None:
        return
    return int(value)


def to_float_if_defined(value):
    if value == "" or value is None:
        return
    return float(value)


SentryOption = collections.namedtuple("SentryOption", ["key", "default", "converter"])

# Mapping of Odoo logging level -> Python stdlib logging library log level.
LOG_LEVEL_MAP = {
    getattr(odoo.loglevels, f"LOG_{x}"): getattr(logging, x)
    for x in ("CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET")
}
DEFAULT_LOG_LEVEL = "warn"

ODOO_USER_EXCEPTIONS = [
    "odoo.exceptions.AccessDenied",
    "odoo.exceptions.AccessError",
    "odoo.exceptions.DeferredException",
    "odoo.exceptions.MissingError",
    "odoo.exceptions.RedirectWarning",
    "odoo.exceptions.UserError",
    "odoo.exceptions.ValidationError",
    "odoo.exceptions.Warning",
    "odoo.exceptions.except_orm",
]
DEFAULT_IGNORED_EXCEPTIONS = ",".join(ODOO_USER_EXCEPTIONS)

EXCLUDE_LOGGERS = ("werkzeug",)
DEFAULT_EXCLUDE_LOGGERS = ",".join(EXCLUDE_LOGGERS)

DEFAULT_ENVIRONMENT = "develop"


def get_sentry_logging(level=DEFAULT_LOG_LEVEL):
    if level not in LOG_LEVEL_MAP:
        level = DEFAULT_LOG_LEVEL

    return LoggingIntegration(
        # Gather warnings into breadcrumbs regardless of actual logging level
        level=logging.WARNING,
        event_level=LOG_LEVEL_MAP[level],
    )


def _get_default(key, fallback=None):
    """Retrieves a default value from sentry_sdk DEFAULT_OPTIONS defensively.

    The keys available in DEFAULT_OPTIONS may change between sentry_sdk versions,
    so a fallback is provided for each option.
    """
    return DEFAULT_OPTIONS.get(key, fallback)


def get_sentry_options():
    res = [
        SentryOption("dsn", "", str.strip),
        SentryOption("logging_level", DEFAULT_LOG_LEVEL, get_sentry_logging),
        SentryOption(
            "include_local_variables",
            _get_default("include_local_variables", False),
            None,
        ),
        SentryOption(
            "max_breadcrumbs",
            _get_default("max_breadcrumbs", 100),
            to_int_if_defined,
        ),
        SentryOption("release", _get_default("release"), None),
        SentryOption("environment", _get_default("environment"), None),
        SentryOption("server_name", _get_default("server_name"), None),
        SentryOption("shutdown_timeout", _get_default("shutdown_timeout", 2), None),
        SentryOption(
            "in_app_include",
            _get_default("in_app_include", []),
            split_multiple,
        ),
        SentryOption(
            "in_app_exclude",
            _get_default("in_app_exclude", []),
            split_multiple,
        ),
        SentryOption(
            "default_integrations",
            _get_default("default_integrations", True),
            None,
        ),
        SentryOption("dist", _get_default("dist"), None),
        SentryOption(
            "sample_rate",
            _get_default("sample_rate", 1.0),
            to_float_if_defined,
        ),
        SentryOption("send_default_pii", _get_default("send_default_pii", False), None),
        SentryOption("http_proxy", _get_default("http_proxy"), None),
        SentryOption("https_proxy", _get_default("https_proxy"), None),
        SentryOption("ignore_exceptions", DEFAULT_IGNORED_EXCEPTIONS, split_multiple),
        SentryOption(
            "max_request_body_size",
            _get_default("max_request_body_size", "medium"),
            None,
        ),
        SentryOption(
            "max_value_length",
            _get_default("max_value_length", 1024),
            to_int_if_defined,
        ),
        SentryOption(
            "attach_stacktrace", _get_default("attach_stacktrace", False), None
        ),
        SentryOption("ca_certs", _get_default("ca_certs"), None),
        SentryOption("propagate_traces", _get_default("propagate_traces", True), None),
        SentryOption(
            "traces_sample_rate",
            _get_default("traces_sample_rate"),
            to_float_if_defined,
        ),
    ]

    if "auto_enabling_integrations" in DEFAULT_OPTIONS:
        res.append(
            SentryOption(
                "auto_enabling_integrations",
                DEFAULT_OPTIONS["auto_enabling_integrations"],
                None,
            )
        )

    return res
