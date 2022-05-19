Select level:
=============
#. Go to *Settings > General Settings> Permission section*.
#. Choose the level of *Restrict Delete Attachment* (strict by default).

Three levels:
=============
* Strict : Owner and admins only (by default)
* Custom : Certain groups or users per related model.
* Custom + Strict : Owner, admins and Certain groups or users per related model.
* None : all users can delete them

Only Custom and Custom + Strict need specific configuration.

For Custom and Custom + Strict levels:
======================================
#. Go to *Settings > Techinical > Database Structure > Models*.
#. Open a model for which attachment deletion should be restricted.
#. Select 'Restrict Attachment Deletion', and assign 'Attachment Deletion Groups' and/or
   'Attachment Deletion Users' as necessary (if no assignment, no one can delete the
   attachments of this model).

For assigning 'Attachment Deletion Groups'/'Attachment Deletion Users' to the model,
you can alternatively add the model in the 'Attachment Deletion Models' tab in the
respective group/user form.
