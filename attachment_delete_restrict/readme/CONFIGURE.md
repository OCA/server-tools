## Select level:

1.  Go to *Settings \> General Settings\> Permission section*.
2.  Choose the level of *Restrict Delete Attachment* for all models by
    default or for models with "default" restriction level.

## Five levels:

- Default : Use global configuration
- Owner : Owner and admins only
- Custom : Certain groups or users per related model.
- Owner + Custom : Owner, admins and Certain groups or users per related
  model.
- None : all users can delete them

Only Custom and Owner + Custom need specific configuration on models.

## For Custom and Owner + Custom levels:

1.  Go to *Settings \> Technical \> Database Structure \> Models*.
2.  Open a model for which attachment deletion should be restricted.
3.  Select 'Restrict Attachment Deletion', and assign 'Attachment
    Deletion Groups' and/or 'Attachment Deletion Users' as necessary (if
    no assignment, no one can delete the attachments of this model).

For assigning 'Attachment Deletion Groups'/'Attachment Deletion Users'
to the model, you can alternatively add the model in the 'Attachment
Deletion Models' tab in the respective group/user form.
