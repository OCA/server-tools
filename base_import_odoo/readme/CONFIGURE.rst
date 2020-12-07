Go to Settings / Remote Odoo import / Import configurations and create a configuration.

After filling in your credentials, select models you want to import from the remote database. If you only want to import a subset of the records, add an appropriate domain.

The import will copy records of all models listed, and handle links to records of models which are not imported depending on the existing field mappings. Field mappings to local records also are a stopping condition. Without those, the import will have to create some record for all required x2x fields, which you probably don't want.

Probably you'll want to map records of model ``res.company``, and at least the admin user.

The module doesn't import one2many fields, if you want to have those, add the model the field in question points to to the list of imported models, possibly with a domain.

If you don't fill in a remote ID, the addon will use the configured local ID for every record of the model (this way, you can for example map all users in the remote system to some import user in the current system).

For fields that have a uniqueness constraint (like ``res.users#login``), create a field mapping if type ``unique``, then the import will generate a unique value for this field.

For models using references with two fields (like ``ir.attachment``), create a field mapping of type ``by reference`` and select the two fields involved. The import will transform known ids (=ids of models you import) to the respective local id, and clean out the model/id fields for unknown models/ids.

You can add custom defaults per model in case your database has different required fields than the source database. For ``res.partner``, you'll most certainly fill in ``{'name': '/'}`` or somethign similar.
