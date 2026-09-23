This module provides a **generic**, reusable mechanism to **save** and **apply** named templates
that autocomplete any Odoo wizard/form using a **JSON payload** stored in a template record.

It is designed to be **framework-like**: other modules can inherit the mixin and add a few buttons in XML.

---

## What you get

### 1) Template model
`data.autocomplete.template`

Each template stores:
- `name`: template name
- `model_id`: the target Odoo model (`ir.model`) the template applies to
- `company_id`: company scoping (global or per company)
- `user_id`: optional owner (personal templates)
- `values_json`: a JSON dictionary holding serialized default values

### 2) Mixin
`data.template.mixin`

Add it to any wizard/model to get:
- `template_id` field (select a template)
- actions (for buttons):
  - `action_open_create_template_wizard()`
  - `action_update_current_template()`
  - `action_apply_template(overwrite=True)`

### 3) Create Template Wizard
`data.wizard.template.create`

This popup asks for a **name** (and personal/global scope) and creates the template using
the current wizard/model values.

### JSON serialization
The mixin serializes current values into a JSON-safe dict:
- `many2one` -> the record `id` (or `false`)
- `many2many` -> a list of record ids
- basic fields (char/int/float/bool/date/datetime/selection/text/monetary) -> stored as-is
- `one2many` is ignored
- computed fields without inverse and readonly fields are ignored (by default)

### Applying templates safely with onchanges
Applying a template uses a **phased write**:

1. **Drivers**: fields returned by `_template_driver_fields()` are written first  
2. **Rest**: everything else (excluding protected fields)  
3. **Protected**: fields returned by `_template_protected_fields()` are written last

This solves common wizard issues where changing a driver field triggers an onchange that clears
other fields (e.g. changing `plan_id` clears `account_ids`).

While applying, `apply_template=True` is present in the context so you can skip destructive
onchanges in your own code.
