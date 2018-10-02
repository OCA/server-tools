To configure this module, you need to add a section ``[ir.config_parameter]`` to
you server_environment_files configurations, where the keys are the same
as would normally be set in the Systems Parameter Odoo menu.

When first using a value, the system will read it from the configuration file
and override any value that would be present in the database, so the configuration
file has precedence.

When creating or modifying values that are in the configuration file, the
module replace changes, enforcing the configuration value.

For example you can use this module in combination with web_environment_ribbon:

.. code::

   [ir.config_parameter]
   ribbon.name=DEV