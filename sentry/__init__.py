# -*- coding: utf-8 -*-
# Copyright 2016-2017 Versada <https://versada.eu/>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo.service import wsgi_server
from odoo.tools import config as odoo_config

from . import const
from .logutils import LoggerNameFilter, OdooSentryHandler

_logger = logging.getLogger(__name__)
try:
    import raven
    from raven.middleware import Sentry
except ImportError:
    _logger.debug('Cannot import "raven". Please make sure it is installed.')


def get_odoo_commit(odoo_dir):
    '''Attempts to get Odoo git commit from :param:`odoo_dir`.'''
    if not odoo_dir:
        return
    try:
        return raven.fetch_git_sha(odoo_dir)
    except raven.exceptions.InvalidGitRepository:
        _logger.debug(
            u'Odoo directory: "%s" not a valid git repository', odoo_dir)


def initialize_raven(config, client_cls=raven.Client):
    '''
    Setup an instance of :class:`raven.Client`.

    :param config: Sentry configuration
    :param client: class used to instantiate the raven client.
    '''
    options = {
        'release': get_odoo_commit(config.get('sentry_odoo_dir')),
    }
    for option in const.SENTRY_OPTIONS:
        value = config.get('sentry_%s' % option.key, option.default)
        if callable(option.converter):
            value = option.converter(value)
        options[option.key] = value

    client = client_cls(**options)

    enabled = config.get('sentry_enabled', True)
    level = config.get('sentry_logging_level', const.DEFAULT_LOG_LEVEL)
    exclude_loggers = const.split_multiple(
        config.get('sentry_exclude_loggers', const.DEFAULT_EXCLUDE_LOGGERS)
    )
    if level not in const.LOG_LEVEL_MAP:
        level = const.DEFAULT_LOG_LEVEL

    if enabled:
        handler = OdooSentryHandler(
            config.get('sentry_include_context', True),
            client=client,
            level=const.LOG_LEVEL_MAP[level],
        )
        if exclude_loggers:
            handler.addFilter(LoggerNameFilter(
                exclude_loggers, name='sentry.logger.filter'))
        raven.conf.setup_logging(handler)
        wsgi_server.application = Sentry(
            wsgi_server.application, client=client)

    return client


sentry_client = initialize_raven(odoo_config)
sentry_client.captureMessage('Starting Odoo Server')
