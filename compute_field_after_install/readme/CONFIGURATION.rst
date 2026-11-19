This module can be installed just like any other Odoo module, by adding it
to Odoo *addons_path*. In order for the module to work correctly,
it needs to be loaded as a server-wide module.
This can be done with the ``server_wide_modules`` parameter in your Odoo config
file or with the ``--load`` command-line parameter.

Additionnaly you can customize the minimum number of records that will defer the
fields computation by adding the following variable in the odoo config file
``computed_fields_defer_threshold=20000``

You can also customize the batch size of the fields computation by adding
the following variable in the odoo config file
``computed_fields_batch_size=1000`` or more specifically for a model
``computed_fields_batch_size__<model_name>=1000`` and for a specific model field
``computed_fields_batch_size__<model_name>__<field_name>=1000``

i.e.:
``computed_fields_batch_size__res_partner=2000``
``computed_fields_batch_size__res_partner__commercial_company_name=50``
 