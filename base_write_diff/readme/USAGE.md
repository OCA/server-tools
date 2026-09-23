**Summary**

This module allows you to update records by filtering out fields whose values are going
to be left unchanged by ``BaseModel.write()``; for example, let's assume you have:

```python
>>> self
sale.order.line(1,)
>>> self.price_unit
10.00
```

If you use ``self.write({"price_unit": 10.00})`` or ``self.price_unit = 10.00``, Odoo
may end up executing unnecessary operations, like triggering the update on the field,
recompute computed fields that depend on ``price_unit``, and so on, even if the value
is actually unchanged.

By using this module, you can prevent all of that.

You can use this module in 3 different ways. All of them require you to add this module
as a dependency of your module.

**1 - Context key ``"write_use_diff_values"``**

By adding ``write_use_diff_values=True`` to the context when updating a field value,
 the ``BaseModel.write()`` patch will take care of filtering out the fields' values
 that are the same as the record's current ones.

⚠️ Beware: the context key is propagated down to other ``write()`` calls

Example:

```python
from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def write(self, vals):
        # Update only fields that are actually different
        self = self.with_context(write_use_diff_values=True)
        return super().write(vals)


class ProductProduct(models.Model):
    _inherit = "product.product"

    def update_code_if_necessary(self, code: str):
        # Update ``default_code`` only if different from the current value
        self.with_context(write_use_diff_values=True).default_code = code
```

**2 - Method ``BaseModel.write_diff()``**

It is the same as calling ``write()``, but it automatically enables the
 ``"write_use_diff_values"`` context flag: ``self.write_diff(vals)`` is a shortcut for
 ``self.with_context(write_use_diff_values=True).write(vals)``

⚠️ Beware: the context key is propagated down to other ``write()`` calls

**3 - Method ``BaseModel._get_write_diff_values(vals)``**

This method accepts a write-like ``dict`` as param, and returns a new ``dict`` made of
 the fields who will actually update the record's values. This allows for a more
 flexible and customizable behavior than the context key usage, because:

- you'll be able to filter out specific fields, instead of filtering out all the fields
  whose values won't be changed after the update;
- you'll be able to execute the filtering on specific models, instead of executing it
  on all the models involved in the stack of ``write()`` calls from the first usage of
  the context key down to the base method ``BaseModel.write()``.

Example:

```python
from collections import defaultdict

from odoo import api, models
from odoo.tools.misc import frozendict


class ProductProduct(models.Model):
    _inherit = "product.product"

    def write(self, vals):
        # OVERRIDE: ``odoo.addons.product.models.product_product.Product.write()``
        # override will clear the whole registry cache if either 'active' or
        # 'product_template_attribute_value_ids' are found in the ``vals`` dictionary:
        # remove them unless it's necessary to update them
        fnames = {"active", "product_template_attribute_value_ids"}
        if vals_to_check := {f: vals.pop(f) for f in fnames.intersection(vals)}:
            groups = defaultdict(lambda: self.browse())
            for prod in self:
                groups[frozendict(prod._get_write_diff_values(vals_to_check))] += prod
            for diff_vals, prods in groups.items():
                if res_vals := (vals | dict(diff_vals)):
                    super(ProductProduct, prods).write(res_vals)
            return True
        return super().write(vals)
```
