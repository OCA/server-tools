Validating some operations is a common need across different areas in a
company and sometimes it also involves several people and stages in the
process. With this module you will be able to define your custom
validation workflows for any Odoo document.

This module does not provide a functionality by itself but an abstract
model to implement a validation process based on tiers on other models
(e.g. purchase orders, sales orders, budgets, expenses...).

**Note:** To be able to use this module in a new model you will need
some development.

See [purchase_tier_validation](https://github.com/OCA/purchase-workflow)
as an example of implementation.

Additionally, if your state field is a (stored) computed field, you need to
set `_tier_validation_state_field_is_computed` to `True` in your model Python
file, and you will want to add the dependent fields of the compute method
in `_get_after_validation_exceptions` and `_get_under_validation_exceptions`.
