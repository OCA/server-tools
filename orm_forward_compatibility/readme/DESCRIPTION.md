This module backports a subset of the Odoo 19+ ORM API onto Odoo 18.0.
Backporting a module to 18.0 then requires fewer adaptations.

Backported so far:

- `Domain`, the domain object introduced in Odoo 19.
- The typed `ir.config_parameter` getters `get_str`, `get_int`, `get_float` and
  `get_bool`, which return a typed value or a default instead of `False`.
