Menu: "Settings/Technical/Time Parameters"

Create a parameter with different versions (start date and value).

If model_id is empty, any model/record may get the time parameter.

The value may be a text or, for the "Record" type, a reference.

The value is parsed according to the type of the parameter when it is
stored, so a version that the type cannot read is refused instead of
failing later, when the parameter is used.

Get the value like this:

``` python
# Pass no date: using today's date
value = model.get_time_parameter("parameter_code_or_name")
# Pass a date or datetime
value = model.get_time_parameter("parameter_code_or_name", date=datetime.datetime.now()))
# Pass the name of a date/datetime field of the record
value = record.get_time_parameter("parameter_code_or_name", "date")
# Raise instead of returning None when there is no value at that date
value = model.get_time_parameter("parameter_code_or_name", raise_if_not_found=True)
```

## Which parameter is used

Several parameters may share the same code, and the most specific one
wins:

1.  a parameter of the current company beats a parameter with no company
    (a global one),
2.  a parameter of the model asking for it beats a parameter with no
    model (one that applies to any model).

So a module may ship a global parameter as a default value, and a
company may override it by creating its own parameter with the same
code. If the winning parameter has no version starting before the
requested date, the next one is used.

## Example of implementation in another module

Payroll implementation:

- Menu "Payroll/Configuration/Time Parameters" only shows hr.payslip
  parameters.
- New parameters will be hr.payslip parameters.
- By default, the model_id field is hidden in the form.

``` XML
<record id="base_time_parameter_action" model="ir.actions.act_window">
    <field name="name">Time Parameters</field>
    <field name="res_model">base.time.parameter</field>
    <field name="view_mode">tree,form</field>
    <field
        name="domain"
        eval="[('model_id', '=', ref('payroll.model_hr_payslip'))]"
    />
    <field
        name="context"
        eval="{'default_model_id': ref('payroll.model_hr_payslip')}"
    />
</record>
<menuitem
    id="menu_action_base_time_parameter"
    action="base_time_parameter_action"
    name="Time Parameters"
    parent="payroll_menu_configuration"
    sequence="35"
/>
```

Reference field implementatiton:

``` python
from odoo import fields, models


class TimeParameterVersion(models.Model):
    _inherit = "base.time.parameter.version"

    value_reference = fields.Reference(
        selection_add=[("account.account", "Account")],
    )
```
