# coding: utf-8
import logging
from logging.config import DictConfigurator

import odoo
import odoo.tools.config as odoo_config


MAX_VALUE_SIZE = 10000  # maximum size of a value in a method param
DEFAULT_FILTER_METHODS = 'call,call_kw,call_button'


def _convert_datatypes(cfg):
    new_cfg = dict(cfg)
    for key, value in new_cfg.iteritems():
        if isinstance(value, basestring) and value.isdigit():
            new_cfg[key] = int(value)
    return new_cfg


def logger():
    handler_cfg = odoo.tools.config.misc.get('audit_log')
    if handler_cfg:
        cfg = {}
        handler_cfg = _convert_datatypes(handler_cfg)

        if 'formatter_class' in handler_cfg:
            formatter_cfg = {'()': handler_cfg['formatter_class']}
            del handler_cfg['formatter_class']
        elif 'format' in handler_cfg:
            formatter_cfg = {'format': handler_cfg['format']}
            del handler_cfg['format']
        else:
            formatter_cfg = None

        if formatter_cfg:
            formatter = DictConfigurator({}).configure_formatter(formatter_cfg)
            cfg['formatters'] = {'audit': formatter}
            handler_cfg['formatter'] = 'audit'
        audit_handler = DictConfigurator(cfg).configure_handler(handler_cfg)
        audit_logger = logging.getLogger(__name__)
        audit_logger.propagate = False
        audit_logger.addHandler(audit_handler)
        return audit_logger
    elif not odoo_config['stop_after_init']:
        test_mode = odoo_config['test_enable'] or odoo_config['test_file']
        log_level = logging.INFO if test_mode else logging.WARNING
        logging.log(log_level, "Audit Log Handler not configured, not logging")


def filter_methods():
    methods = odoo.tools.config.get_misc(
        'audit_log', 'filter_methods', DEFAULT_FILTER_METHODS)
    return methods.split(',')
