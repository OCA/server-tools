First give your user the access right "Manage Time Parameters".
Then you can create new parameters in "Settings/Technical/Time Dependent Parameters".

The parameters need a code and a description (which is optional). Then you can create new versions of this parameters
when you define a "from_date" and a value.

Then you can access current parameter value like this:
.. code-block:: python
    # using today's date when no date is passed

    value = model.get_time_dependent_parameter('my_parameter_name')

    # hr.payslip: use payslip.date_to

    value = payslip.get_time_dependent_parameter('my_parameter_name', payslip.date_to)

    # account.tax: use tax_date (https://github.com/apps2grow/apps/tree/14.0/account_tax_python_with_date)

    tax_rate = float(company.get_time_dependent_parameter('tax_high_rate', tax_date))

Finally i recomend that if you use this parameters in another modules, you create a view which filter by module_name so
you can have a view for each module that needs to change this parameters and the user can only view the parameters
of the module that he is looking to change.

Note: You can see a usage case of this module in OCA Payroll Module.
More information in this PR: https://github.com/OCA/payroll/pull/31
