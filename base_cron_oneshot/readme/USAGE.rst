You can create crons as usual via the admin interface or via code.
The important thing, in both case, is to set `oneshot` flag as true.

**Developer shortcut**

You can easily create a oneshot cron like this:

.. code-block:: python

  cron = self.env['ir.cron'].schedule_oneshot(
      'res.partner', method='my_cron_method')

If you need to customize other parameters you can pass them as keyword args:

.. code-block:: python

  my_values = {...}
  cron = self.env['ir.cron'].schedule_oneshot(
      'res.partner', method='my_cron_method', **my_values)
