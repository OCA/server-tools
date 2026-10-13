After installation of this module, go to the Settings menu -\> Technical
-\> Database cleanup. This menu is only available to members of the
*Settings* group. Go through the modules, models, columns and
tables entries under this menu (in that order) and find out if there is
orphaned data in your database. You can either delete entries by line,
or sweep all entries in one big step (if you are *really* confident).

Always back up both the database and its filestore before purging data.

When purging a model in Odoo 20.0, ordinary attachments returned by the
attachment search are detached from the model. Attachments stored for binary
fields are excluded from that search. Access rules can also hide attachments
whose model no longer exists. Odoo deletes any attachments still linked to the
purged model, including field attachments, and schedules their stored files for
garbage collection. Unlike in 19.0, field attachments therefore do not survive
the model purge.

Model and field purges use `force_delete=True` to allow removal of non-manual
metadata. This does not simulate a module uninstall: Odoo 20.0 still executes
`@api.ondelete(at_uninstall=False)` hooks, which can prevent a purge. The module
does not bypass these hooks.

[![Try me on Runbot](https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas)](https://runbot.odoo-community.org/runbot/149/11.0)
