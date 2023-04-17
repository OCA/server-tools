This module lets you log slow WSGI requests. It is useful to analysis
performance issue given more context regarding the request and
only log if processed time is higher to the defined limit.

.. warning::

    This module may leak confidential data in the log. Use with care.
