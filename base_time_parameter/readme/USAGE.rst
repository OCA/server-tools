Menu: "Settings/Technical/Time Parameters"

Create a parameter with different versions (start date and value).

If model_id is empty, any model/record may get the time parameter.

The value may be a text or reference.

Get the value like this:

.. code-block:: python

    # Pass no date: using today's date
    value = model.get_time_parameter("parameter_code_or_name")
    # Pass a date or datetime
    value = model.get_time_parameter("parameter_code_or_name", date=datetime.datetime.now()))
    # Pass the name of a date/datetime field of the record
    value = record.get_time_parameter("parameter_code_or_name", "date")

Example of implementation in another module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Payroll implementation:

* Menu "Payroll/Configuration/Time Parameters" only shows hr.payslip parameters.
* New parameters will be hr.payslip parameters.
* By default, the model_id field is hidden in the form.

.. code-block:: XML

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

Reference field implementatiton:

.. code-block:: python

    from odoo import fields, models


    class TimeParameterVersion(models.Model):
        _inherit = "base.time.parameter.version"

        value_reference = fields.Reference(
            selection_add=[("account.account", "Account")],
        )
