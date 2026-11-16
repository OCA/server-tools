Inherit the mixin and set the field and size of each side of the window:

```python
class SensorReading(models.Model):
    _name = "sensor.reading"
    _inherit = "search.date.window.mixin"

    # lower bound: date >= now - 7 days
    _date_window_past_field = "date"
    _date_window_past_days = 7
    # upper bound: date < now + 1 day
    _date_window_future_field = "date"
    _date_window_future_days = 1

    date = fields.Datetime(required=True, index=True)
```

A side with no field or with `None` days is not applied. Both sides can use
different fields, for instance a start date for the past and an end date for
the future. `Date` and `Datetime` fields are supported.

The window applies to `search()`, `search_count()`, `search_read()`,
`read_group()` and to many2many reads, because all of them build their
query through `_where_calc()`.

A side of the window is not added when the domain already has:

- a condition on one of the window fields with `>`, `>=` or `=` (past side)
  or with `<`, `<=` or `=` (future side);
- a condition on `id`, with any operator.

To disable the window, set the `date_window_test` key to `False` in the
context, as with `active_test`:

```python
self.env["sensor.reading"].with_context(date_window_test=False).search([])
```

The name of the key can be changed per model with `_date_window_context_key`.

The window is not applied, unless the context sets the key explicitly:

- when a relational field is read by attribute access on a record of the
  model (`record.child_ids`);
- when Odoo looks for the records whose stored computed fields depend on a
  record of the model that has changed, so old records don't keep stale
  values.

