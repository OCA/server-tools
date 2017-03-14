# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp (http://www.camptocamp.com).
# @author Guewen Baconnier <guewen.baconnier@camptocamp.com>
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import os
import threading
import re

from distutils.util import strtobool

_logger = logging.getLogger(__name__)

try:
    from pythonjsonlogger import jsonlogger
except ImportError:
    jsonlogger = None  # noqa
    _logger.debug("Cannot 'import pythonjsonlogger'.")


def is_true(strval):
    return bool(strtobool(strval or '0'.lower()))

# The following regex are use to extract information from native odoo log
# We struct is the following
# {name_of_the_log : [regex, formatter, extra_vals]}
# The extra_vals "dict" will be merged into the jsonlogger if the regex match
# In order to make understandable the regex please add an string example that
# match

REGEX = {
    'openerp.addons.base.ir.ir_cron': [
        # "cron.object.execute('db', 1, '*', u'base.action.rule', u'_check')"
        ("cron\.object\.execute\('.+'(?P<cron_model>[\w.]+).+"
         "'(?P<cron_method>[\w.]+)'\)",
         {}, {'cron_running': True}),

        # "0.016s (base.action.rule, _check)"
        ("(?P<cron_duration_second>[\d.]+)s \("
         "(?P<cron_model>[\w.]+), (?P<cron_method>[\w.]+)",
         {'cron_duration_second': float},
         {'cron_running': False, 'cron_status': 'succeeded'}),

        # Call of self.pool.get('base.action.rule')._check(
        # cr, uid, *u'()') failed in Job 43
        ("Call of self\.pool\.get\('(?P<cron_model>[\w.]+)'\)"
         ".(?P<cron_method>[\w.]+)",
         {}, {'cron_running': False, 'cron_status': 'failed'}),
    ],
}


class OdooJsonFormatter(jsonlogger.JsonFormatter):

    def add_fields(self, log_record, record, message_dict):
        record.pid = os.getpid()
        record.dbname = getattr(threading.currentThread(), 'dbname', '?')
        _super = super(OdooJsonFormatter, self)
        res = _super.add_fields(log_record, record, message_dict)
        if log_record['name'] in REGEX:
            for regex, formatters, extra_vals in REGEX[log_record['name']]:
                match = re.match(regex, log_record['message'])
                if match:
                    vals = match.groupdict()
                    for key, func in formatters.items():
                        vals[key] = func(vals[key])
                    log_record.update(vals)
                    if extra_vals:
                        log_record.update(extra_vals)
        return res


if is_true(os.environ.get('ODOO_LOGGING_JSON')):
    format = ('%(asctime)s %(pid)s %(levelname)s'
              '%(dbname)s %(name)s: %(message)s')
    formatter = OdooJsonFormatter(format)
    logging.getLogger().handlers[0].formatter = formatter
