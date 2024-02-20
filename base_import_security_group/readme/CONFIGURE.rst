To allow a user to import data from CSV and Excel files, just follow this steps:

* Go to *Settings/Users/Users* menu.
* Enter the user you want to allow.
* Within the "Access Rights" tab and "Technical Settings" group, check the
  option "Import CSV/Excel files (all models)".

Alternatively, to allow a user to import **only** on specific models (ex. Contacts) and not
on others:

* Activate the developer mode in *Settings*.
* Go to *Settings/Users/Groups*.
* Create a new group (name: "Allow import for Contacts only", application: "Technical Settings").
* Go to *Settings/Technical/Database Structure/Models*.
* Search for model=res.partner and select the model.
* Set the "Import Group" field to "Allow import for Contacts only".
* Go to *Settings/Users/Users* menu.
* Enter the user you want to allow.
* Within the "Access Rights" tab and "Technical Settings" group, check the
  option "Allow import for Contacts only".
