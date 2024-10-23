In Odoo's configuration file, add the ``audit_log`` section. The keys are the
same as in Python's logging handler configuration, plus three extra (optional):

   - ``format``: log format as used by Python's ``logging`` (default formatter's one if omitted)
   - ``formatter_class``: complete path of a Formatter class
   - ``filter_methods``: Odoo Request methods to be logged, separated by commas. Default: ``call,call_kw,call_button``

This module adds some extra attributes to logRecord that you can combine with the standard ones:

  - ``dbname``: %(dbname)s
  - ``method``: %(method)s
  - ``params``: %(params)s
  - ``uid``: %(uid)d
  - ``timestamp``: %(timestamp)s (UTC, compararable to asctime)
  - ``exception``: %(exception)s

Rq:
  - %(message)s = 'AUDIT'



Example::

    [audit_log]
    class = logging.FileHandler
    filename = /tmp/audit.log
    formatter_class = logging.Formatter
    format = %(timestamp)s %(message)s %(dbname)s %(method)s | %(uid)d | %(params)s | %(exception)s
