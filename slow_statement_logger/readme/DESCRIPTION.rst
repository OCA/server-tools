This module lets you log slow SQL statements. It is useful when you don't have
access to the PostgreSQL log or when it is difficult to correlate the
PostgreSQL log with the Odoo log.

.. warning::

    This module may leak confidential data in the log, in a similar way
    to Odoo's ``--log-level=debug_sql`` option. Use with care.
