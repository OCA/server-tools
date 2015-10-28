.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=================
Module Prototyper
=================

This module allows the administrator to prototype new features and export them as module. 
Functional people can prepare the job for a developer who is left with the logic to implement 
in addition to everything the prototype does not export yet.

Installation
============

Make sure you have Jinja2 version 2.7.3 or higher installed::

$ pip install --upgrade Jinja2==2.7.3

Configuration
=============

No configuration required.

Usage
=====

To use this module, you need to:

* install the dependencies of your future module
* customize your instance by adding fields and creating inherited views
* create your menu items and their window actions
* prepare your data and demo data by creating filters
* create your own groups with access rights and record rules
* add your own access rights and record rules to an existing group

Once you have customized your instance properly, you can go to Settings > Module Prototypes > Prototypes
and create a new prototype:

* fill in the information of your module (enter the name, the description, the logo, etc.)
* in the Depencencies tab, select all the other modules that yours will be depending on
* in the Data & Demo tab, select your filters for data and demo data
* in the Fields tab, select the fields you created or customized
* in the Interface tab, select your menu items and your views
* in the Security tab, select your groups, access rights and record rules
* save and click on export

You will get a zip file containing your module ready to be installed and compliant with the 
conventions of the OCA. You can then provide the module to a developer who have to implement 
things like default values or onchange methods.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/149/8.0

Known issues / Roadmap
======================

* `#104`_ - Include controllers.py and templates.xml from scaffold.
* Attach images to the prototype and export them to be used in the 'images' module manifest.
* Export data and demo data
* Export reports
* Export workflows, nodes, transitions, actions
* Export groups, access rights and record rules
* Allow selecting and exporting website stuff

.. _#104: https://github.com/OCA/server-tools/issues/104

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/server-tools/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/server-tools/issues/new?body=module:%20module_prototyper%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* David Arnold <blaggacao@users.noreply.github.com>
* Jordi Riera <jordi.riera@savoirfairelinux.com>
* Maxime Chambreuil <maxime.chambreuil@savoirfairelinux.com>
* El hadji Dem <elhadji.dem@savoirfairelinux.com>
* Savoir-faire Linux <support@savoirfairelinux.com>
* Vincent Vinet <vincent.vinet@savoirfairelinux.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.

Changelog
=========

v0.3
----

* Replace ir.ui.model by ir.ui.view in generated xml views
* Improve pep8 compatibility of generation of models

v0.2
----

* Renamed from prototype to module_prototyper as discussed in #108
* Menu in Settings that gather element used to create a prototype (menu views, views, fields)

v0.1
----

* The set up of openerp.py is covered, description, maintainer, website, name, technical name...
* Views and menus can be set through odoo and gathered in prototype. The files will be automatically generated and add to the data section of the openerp.py. Be aware some advanced feature as domain or context might still missing.
* Dependencies can be set through the Dependencies tab
* Custom fields can be added. A file by model will be generated with all the fields of the model. The init.py files are updated accordingly. Be aware that some features are not implemented yet, as the domain, the context.
