After installation of this module, go to the Settings menu -\> Technical
-\> Database cleanup. This menu is only available to members of the
*Access Rights* group. Go through the modules, models, columns and
tables entries under this menu (in that order) and find out if there is
orphaned data in your database. You can either delete entries by line,
or sweep all entries in one big step (if you are *really* confident).

If there are so many orphaned data entries that purging them all at once is
too slow, use *Purge obsolete data entries in batches* instead. This wizard
scans the data entries, shows one progress line per model and deletes the
orphaned entries in batches, committing after every batch. Use *Purge next
batch* to delete a single batch, or *Purge all (in batches)* to let the wizard
loop until everything is cleaned up.

[![Try me on Runbot](https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas)](https://runbot.odoo-community.org/runbot/149/11.0)
