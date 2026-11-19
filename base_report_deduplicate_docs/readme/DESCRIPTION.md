This module adds the possibility of printing records data only once when a record ID is
 passed to ``ir.actions.report._render*()`` functions.

If you have a report with this template's architecture:
```html
<t t-foreach="docs" t-as="doc">
    <!-- content -->
</t>
```
and Odoo calls `report._render([1, 1, 1], data=...)`, the resulting output will be a
 triple copy of the same content.

If "Deduplicate Documents" is activated, the resulting output will display it only once,
 because ``docs`` will be cleared of duplicates before Odoo processes the template.
