# coding: utf-8
from datetime import datetime

import odoo

from . import config
from .config import MAX_VALUE_SIZE

audit_logger = config.logger()
filter_methods = config.filter_methods()


def restrict_dict(o):
    new = {}
    for key, value in o.iteritems():
        if isinstance(value, basestring) and 'passw' in key:
            new[key] = 'PASSWORD_CENSORED'
        elif isinstance(value, basestring) and len(value) > MAX_VALUE_SIZE:
            new[key] = '%s...' % value[:MAX_VALUE_SIZE]
        elif isinstance(value, dict):
            new[key] = restrict_dict(value)
        else:
            new[key] = value
    return new


if audit_logger:
    old_call_function = odoo.http.WebRequest._call_function

    def call_function(self, *args, **kw):
        try:
            exception = None
            return old_call_function(self, *args, **kw)
        except Exception as e:
            exception = repr(e)
            raise
        finally:
            method = self.endpoint.method.__name__
            if method in filter_methods:
                log_record = {
                    'dbname': self.db,
                    'method': method,
                    'params': restrict_dict(self.params),
                    'uid': self.session.uid,
                    'timestamp': datetime.utcnow().isoformat(),
                    'exception': exception,
                }
                audit_logger.info("AUDIT", extra=log_record)

    odoo.http.WebRequest._call_function = call_function
