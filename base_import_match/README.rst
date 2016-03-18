.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=================
Base Import Match
=================

By default, when importing data (like CSV import) with the ``base_import``
module, Odoo follows this rule:

#. If you import the XMLID of a record, make an **update**.
#. If you do not, **create** a new record.

This module allows you to set additional rules to match if a given import is an
update or a new record.

This is useful when you need to sync heterogeneous databases, and the field you
use to match records in those databases with Odoo's is not the XMLID but the
name, VAT, email, etc.

After installing this module, the import logic will be changed to:

#. If you import the XMLID of a record, make an **update**.
#. If you do not:
   #. If there are import match rules for the model you are importing:
       #. Discard the rules that require fields you are not importing.
       #. Traverse the remaining rules one by one in order to find a match in
          the database.
          #. If one match is found:
             #. Stop traversing the rest of valid rules.
             #. **Update** that record.
          #. If zero or multiple matches are found:
             #. Continue with the next rule.
          #. If all rules are exhausted and no single match is found:
             #. **Create** a new record.
   #. If there are no match rules for your model:
      #. **Create** a new record.

Configuration
=============

To configure this module, you need to:

#. Go to *Settings > Technical > Database Structure > Import Match*.
#. *Create*.
#. Choose a *Model*.
#. Choose the *Fields* that conform an unique key in that model.
#. *Save*.

In that list view, you can sort rules by drag and drop.

Usage
=====

To use this module, you need to:

#. Follow steps in **Configuration** section above.
#. Go to any list view.
#. Press *Import* and follow the import procedure as usual.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/149/8.0

Roadmap / Known Issues
======================

* Add a filter to let you apply some rules only to incoming imports that match
  a given criteria (like a domain, but for import data).
* Matching by VAT for ``res.partner`` records will only work when the partner
  has no contacts, because otherwise Odoo reflects the parent company's VAT in
  the contact, and that results in multiple matches. Fixing the above point
  should make this work.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/server-tools/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed `feedback
<https://github.com/OCA/
server-tools/issues/new?body=module:%20
base_import_match%0Aversion:%20
8.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Jairo Llopis <yajo.sk8@gmail.com>

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
