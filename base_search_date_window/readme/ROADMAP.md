- Only the leaves of the domain are checked, not the boolean operators around
  them. A date condition inside one branch of an `|`, or negated with `!`,
  still counts as a bound and disables that side of the window.
- `read()` and `web_read()` of a one2many field don't go through
  `_fetch_field()`, so the window applies to the records they return. Add
  `context="{'date_window_test': False}"` to the field if all the records
  are needed.
- The exceptions for relational fields and stored computed fields only apply
  when the record read or modified belongs to a model with the mixin. When a
  record of another model changes, the search for its dependent records in a
  windowed model still applies the window.
