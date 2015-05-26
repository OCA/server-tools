Module Prototype
================

This module allows the administrator to prototype new features and export them as module. 
Functional people can prepare the job for a developer who is left with the logic to implement 
in addition to everything the prototype does not export yet.

Installation
============

No installation steps required other than installing the module itself.

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

Once you have customized your instance properly, you can go to Settings > Modules > Prototype
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

Known issues / Roadmap
======================

 * `#104`_ - Include controllers.py and templates.xml from scaffold.
 * Attach images to the prototype and export them to be used in the 'images' module manifest.
 * Add a Report tab to select and export reports
 * Add a Workflow tab to select and export workflows, nodes, transitions, actions

.. _#104: https://github.com/OCA/server-tools/issues/104

Please report any idea or issue to https://github.com/OCA/server-tools/issues.

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

Versions
========

v0.1
----

All the features are not implemented but the minimal is done.
With this version you can:

    The set up of openerp.py is covered, description, maintainer, website, name, technical name...
    Views and menus can be set through odoo and gathered in prototype. The files will be automatically generated and add to the data section of the openerp.py. Be aware some advanced feature as domain or context might still missing.
    Dependencies can be set throught the Dependency page
    Custom fields can be added. A file by model will be generated with all the fields of the model. The init.py files are updated accordingly. Be aware that some features are not implemented yet, as the domain, the context.

This version should be enought for:

    set up the client module
    create a new field in a view.

Features that you might expect in next version:

    better generation of fields (many2many fields, domain, context)
    Generation of data and demo data files.
    Security files (rules, ir.model.access.csv)
    openerp's description editing README.rst and index.html
    module screenshots

v0.2
----

    Renamed from prototype to module_prototyper as discussed in #108
    menu in Settings that gather element used to create a prototype (menu views, views, fields)

v0.3
----
    Replace ir.ui.model by ir.ui.view in generated xml views
    Improve pep8 compatibility of generation of models


Known bugs
----------

    icon file extension might be wrong. The extension is hard coded for now. It is planned add Document as dependency to handle it.

