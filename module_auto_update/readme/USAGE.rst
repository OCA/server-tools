The main method provided by this module is ``upgrade_changed_checksum``
on ``ir.module.module``. It runs a database upgrade for all installed
modules for which the hash has changed since the last successful
run of this method. On success it saves the hashes in the database.

The first time this method is invoked after installing the module, it
runs an upgrade of all modules, because it has not saved the hashes yet.
This is by design, priviledging safety. Should this be an issue,
the method ``_save_installed_checksums`` can be invoked in a situation
where one is sure all modules on disk are installed and up-to-date in the
database.

To invoke the upgrade mechanism, navigate to *Apps* menu and use the
*Auto-Upgrade Modules* button, available only in developer mode. Restarting
the Odoo instance is highly recommended to minify risk of any possible issues.

Another easy way to invoke this upgrade mechanism is by issuing the following
in an Odoo shell session:

.. code-block:: python

  env['ir.module.module'].upgrade_changed_checksum()
