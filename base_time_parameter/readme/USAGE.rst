First give your user the access right "Manage Time Parameters".
Then in "Settings/Technical/Time Parameters" you can create a new parameter
with different versions (start date and value).

Then you can access current parameter value like this:
.. code-block:: python

    # using today's date when no date is passed
    value = model.get_time_parameter('my_parameter_name')
    # hr.payslip: use payslip.date_to
    value = payslip.get_time_parameter('my_parameter_name', payslip.date_to)
    # account.tax: use tax_date (https://github.com/apps2grow/apps/tree/14.0/account_tax_python_with_date)
    tax_rate = float(company.get_time_parameter('tax_high_rate', tax_date))

Payroll implementation:
* Payroll configuration only shows payslip parameters.
* By default, the model_id field is hidden in the form.
* Only payslip model/record may call time_parameter(code).

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
