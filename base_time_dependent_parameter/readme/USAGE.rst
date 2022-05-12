You can create new parameters in "Settings/Technical/Time Dependent Parameters".

The parameters need a code and a description (which is optional). Then you can create new versions of this parameters
when you define a "from_date" and a value.

Then you can access current parameter value like this:
.. code-block:: python

    value = record.get_time_dependent_parameter('my_parameter_name') # using today's date, any record or model will work
    value = payslip.get_time_dependent_parameter('my_parameter_name', 'date_to') # date or datetime field of the record

Finally i recomend that if you use this parameters in another modules, you create a view which filter by module_name so
you can have a view for each module that needs to change this parameters and the user can only view the parameters
of the module that he is looking to change.

Note: You can see a usage case of this module in OCA Payroll Module.
More information in this PR: https://github.com/OCA/payroll/pull/31
