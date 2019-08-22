.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=================
Base Import Match
=================

By default, when importing data (like CSV import) with the ``base_import``
module, Odoo follows this rule:

- If you import the XMLID of a record, make an **update**.
- If you do not, **create** a new record.

This module allows you to set additional rules to match if a given import is an
update or a new record.

This is useful when you need to sync heterogeneous databases, and the field you
use to match records in those databases with Odoo's is not the XMLID but the
name, VAT, email, etc.

After installing this module, the import logic will be changed to:

- If you import the XMLID of a record, make an **update**.
- If you do not:

  - If there are import match rules for the model you are importing:

    - Discard the rules that require fields you are not importing.
    - Traverse the remaining rules one by one in order to find a match in the database.

      - Skip the rule if it requires a special condition that is not
        satisfied.
      - If one match is found:

        - Stop traversing the rest of valid rules.
        - **Update** that record.
      - If zero or multiple matches are found:

        - Continue with the next rule.
      - If all rules are exhausted and no single match is found:

        - **Create** a new record.
  - If there are no match rules for your model:

    - **Create** a new record.

By default 2 rules are installed for production instances:

- One rule that will allow you to update companies based on their VAT, when
  ``is_company`` is ``True``.
- One rule that will allow you to update users based on their login.

In demo instances there are more examples.

Configuration
=============

To configure this module, you need to:

#. Go to *Settings > Technical > Database Structure > Import Match*.
#. *Create*.
#. Choose a *Model*.
#. Choose the *Fields* that conform a unique key in that model.
#. If the rule must be used only for certain imported values, check
   *Conditional* and enter the **exact string** that is going to be imported
   in *Imported value*.

   #. Keep in mind that the match here is evaluated as a case sensitive
      **text string** always. If you enter e.g. ``True``, it will match that
      string, but will not match ``1`` or ``true``.
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
   :target: https://runbot.odoo-community.org/runbot/149/10.0

Known Issues / Roadmap
======================

* Add a setting to throw an error when multiple matches are found, instead of
  falling back to creation of new record.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/server-tools/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Jairo Llopis <yajo.sk8@gmail.com>
* Vicent Cubells <vicent.cubells@tecnativa.com>

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
