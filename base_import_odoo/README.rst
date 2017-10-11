.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

================================
Import from remote Odoo database
================================

This module was written to import data from another Odoo database. The idea is that you define which models to import from the other database, and add eventual mappings for records you don't want to import.

Use cases
=========

- merging databases
- one way sync (needs a bit polishing)
- aggregating management data from distributed systems


Configuration
=============

Go to Settings / Remote Odoo import / Import configurations and create a configuration.

After filling in your credentials, select models you want to import from the remote database. If you only want to import a subset of the records, add an appropriate domain.

The import will copy records of all models listed, and handle links to records of models which are not imported depending on the existing field mappings. Field mappings to local records also are a stopping condition. Without those, the import will have to create some record for all required x2x fields, which you probably don't want.

Probably you'll want to map records of model `res.company`, and at least the admin user.

The module doesn't import one2many fields, if you want to have those, add the model the field in question points to to the list of imported models, possibly with a domain.

If you don't fill in a remote ID, the addon will use the configured local ID for every record of the model (this way, you can for example map all users in the remote system to some import user in the current system).

For fields that have a uniqueness constraint (like `res.users#login`), set the flag `unique`, then the import will generate a unique value for this field.

Usage
=====

To use this module, you need to:

#. go to an import configuration and hit the button ``Run import``
#. be patient, this creates a cronjob which will start up to a minutes afterwards
#. reload the form, as soon as the cronjob runs you'll see a field ``Progress`` that lets you inspect what was imported already
#. note that the cronjob also resets the password as soon as it has read it. So for a subsequent import, you'll have to fill it in again
#. running an import a second time won't duplicate data, it should recognize records imported earlier and just update them

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
    :alt: Try me on Runbot
    :target: https://runbot.odoo-community.org/runbot/149/8.0

Known issues / Roadmap
======================

* Yes of course this duplicates a lot of connector functionality. Rewrite this with the connector framework, probably collaborate with https://github.com/OCA/connector-odoo2odoo
* Do something with workflows
* Support reference fields, while being at it refactor _run_import_map_values to call a function per field type
* Probably it's safer and faster to disable recomputation during import, and recompute all fields afterwards

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/server-tools/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Holger Brunn <hbrunn@therp.nl>

Do not contact contributors directly about help with questions or problems concerning this addon, but use the `community mailing list <mailto:community@mail.odoo.com>`_ or the `appropriate specialized mailinglist <https://odoo-community.org/groups>`_ for help, and the bug tracker linked in `Bug Tracker`_ above for technical issues.

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
