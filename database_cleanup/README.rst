Clean your OpenERP database from remnants of modules, models, columns and
tables left by uninstalled modules (prior to 7.0) or a homebrew database
upgrade to a new major version of OpenERP.

After installation of this module, go to the Settings menu -> Technical ->
Database cleanup. Go through the modules, models, columns and tables
entries under this menu (in that order) and find out if there is orphaned data
in your database. You can either delete entries by line, or sweep all entries
in one big step (if you are *really* confident).

Caution! This module is potentially harmful and can *easily* destroy the
integrity of your data. Do not use if you are not entirely comfortable
with the technical details of the OpenERP data model of *all* the modules
that have ever been installed on your database, and do not purge any module,
model, column or table if you do not know exactly what you are doing.
