After installation of this module, go to the Settings menu -\> Technical
-\> Database cleanup. This menu is only available to members of the
*Settings* group. Go through the modules, models, columns and
tables entries under this menu (in that order) and find out if there is
orphaned data in your database. You can either delete entries by line,
or sweep all entries in one big step (if you are *really* confident).

Always back up both the database and its filestore before purging data.

When purging a model, all ordinary attachments (those not stored for a binary
field) are preserved and detached from the model, including attachments linked
to records that no longer exist. This does not depend on which attachments the
user can see. Attachments belonging to other models are not changed.

Attachments stored for binary fields of the purged model are deleted by Odoo
20.0, and their stored files are scheduled for garbage collection. Unlike in
19.0, these field attachments do not survive the model purge.

Model and field purges use `force_delete=True` to allow removal of non-manual
metadata. This does not simulate a module uninstall: Odoo 20.0 still executes
`@api.ondelete(at_uninstall=False)` hooks, which can prevent a purge. The module
does not bypass these hooks.

[![Try me on Runbot](https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas)](https://runbot.odoo-community.org/runbot/149/11.0)
