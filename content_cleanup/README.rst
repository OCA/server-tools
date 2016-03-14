Clean your Odoo database content
================================

After installation of this module, go to the Settings menu -> Technical ->
Content cleanup. Go through the models under this menu and delete data
contained in them.  This module only deletes the content of the models. It does
not modify the structure of the database in any way.

Caution! This module is potentially harmful and can *easily* destroy the
integrity of your data. If you are not aware of the relationships between
different models you could easily end up removing data you never intended to
remove.
