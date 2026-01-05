### 1) Inherit the mixin in Python

```python
from odoo import models, api

class MyWizard(models.TransientModel):
    _inherit = ["my.wizard.model", "data.template.mixin"]

    # Optional: define drivers/protected fields to survive onchanges
    def _template_driver_fields(self):
        return {"plan_id"}

    def _template_protected_fields(self):
        return {"account_ids", "show_months"}

    @api.onchange("plan_id")
    def _onchange_plan_id(self):
        # Skip destructive behavior when applying templates
        if self.env.context.get("apply_template"):
            return
        return super()._onchange_plan_id()
```

> Note: This module only provides the base.

### 2) Add UI in XML (template selector + buttons)

Insert this into your wizard form view (adapt `inherit_id` and the `xpath`):

```xml
<separator string="Templates"/>
<group col="4">
    <field name="template_id" options="{'no_create': True}"/>

    <button name="action_apply_template"
            type="object"
            string="Apply"
            class="btn btn-secondary"
            icon="fa-check"
            invisible="not template_id"/>

    <button name="action_open_create_template_wizard"
            type="object"
            string="Save as template"
            class="btn btn-secondary"
            icon="fa-save"/>

    <button name="action_update_current_template"
            type="object"
            string="Update template"
            class="btn btn-secondary"
            icon="fa-refresh"
            invisible="not template_id"/>
</group>
```

### 3) Filtering templates further (optional)
If the same wizard model can represent different "types" of reports (e.g. different `report_id`),
you can further restrict the templates shown by overriding:

```python
def _template_domain_extra(self):
    return [("some_field", "=", self.some_field.id)]
```

---

### Notes / Tips
- If you want templates shared across companies, allow `company_id = False` templates (already supported by the domain).
- If you want only personal templates, set `user_id` on every template and adjust the domain.
- If some fields should never be stored (tokens, volatile flags, etc.), override `_template_skip_fields()`.

---
