To configure this module, you need to:

* Configure your server and a passive service in your monitoring tool
  (e.g service ``Odoo Mail Queue`` on host ``MY-SERVER``).

* Declare your NSCA server in the menu Configuration / Technical / NSCA Client / Servers

.. image:: nsca_client/static/description/server.png
   :width: 400 px

* Create NSCA checks in the menu Configuration / Technical / NSCA Client / Checks

.. image:: nsca_client/static/description/check.png
   :width: 400 px

* Code the methods which will be called by the NSCA checks.

Such methods must return a tuple ``(RC, MESSAGE, PERFORMANCE_DATA)`` where ``RC`` is an integer,
``MESSAGE`` a unicode string AND ``PERFOMANCE_DATA`` is a dictionary.
``RC`` values and the corresponding status are:

- 0: OK
- 1: WARNING
- 2: CRITICAL
- 3: UNKNOWN

``PERFORMANCE_DATA`` is not mandatory, so it could be possible to send
``(RC, MESSAGE)``.
Each element of ``PERFORMANCE_DATA`` will be a dictionary that could contain:

- value: value of the data (required)
- max: Max value on the chart
- min: Minimum value on the chart
- warn: Warning value on the chart
- crit: Critical value on the chart
- uom: Unit of Measure on the chart (s - Seconds, % - Percentage, B - Bytes, c - Continuous)

The key of the dictionary will be used as the performance_data label.

E.g:

.. code-block:: python

    class MailMail(models.Model):
        _inherit = 'mail.mail'

        @api.model
        def nsca_check_mails(self):
            mails = self.search([('state', '=', 'exception')])
            if mails:
                return (1, u"%s mails not sent" % len(mails), {
                  'exceptions': {'value': len(mails)}})
            return (0, u"OK", {'exceptions': {'value': len(mails)}})

On the example, the performance data will use the label ``exceptions`` and the
value will be the number of exception of mails.
