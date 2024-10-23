Select level:
=============
#. Go to *Settings > General Settings> Permission section*.
#. Choose the level of *Restrict Delete Attachment* for all models by default or for models with "default" restriction level.

Five levels:
=============
* Default : Use global configuration
* Owner : Owner and admins only
* Custom : Certain groups or users per related model.
* Owner + Strict : Owner, admins and Certain groups or users per related model.
* None : all users can delete them

Only Owner and Custom + Strict need specific configuration on models.

For Custom and Owner + Strict levels:
======================================
#. Go to *Settings > Technical > Database Structure > Models*.
#. Open a model for which attachment deletion should be restricted.
#. Select 'Restrict Attachment Deletion', and assign 'Attachment Deletion Groups' and/or
   'Attachment Deletion Users' as necessary (if no assignment, no one can delete the
   attachments of this model).

For assigning 'Attachment Deletion Groups'/'Attachment Deletion Users' to the model,
you can alternatively add the model in the 'Attachment Deletion Models' tab in the
respective group/user form.
