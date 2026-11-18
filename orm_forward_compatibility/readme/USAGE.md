**Domain**

Replace the Odoo 19 import `from odoo.fields import Domain` and leave the rest untouched:

``` python
from odoo.addons.orm_forward_compatibility import Domain

domain = Domain("partner_id", "=", partner.id) & Domain([("state", "=", "done")])
```

Not supported yet:
- Relative-date literals
- custom SQL domains
-  `any!` / `not any!` operators

**Typed ir.config_parameter getters**

``` python
limit = self.env["ir.config_parameter"].sudo().get_int("my_module.limit", 20)
```
