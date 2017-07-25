.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===================================================
Fuzzy search using the PostgreSQL trigram extension
===================================================

This addon adds the new search operator `%` in search domains. Currently
this module doesn't change the backend search or anything else. It provides
only the possibilty to perfrom the fuzzy search for external addons.


Installation
============

#. The PostgreSQL extension ``pg_trgm`` should be available. See the README of
   base_trigram_index.


Configuration
=============

If the odoo module is installed:

#. You can define ``GIN`` and ``GiST`` indexes for `char` and `text` fields.
   See the README of base_trigram_index.


Usage
=====

#. You can create an index for the `name` field of `res.partner`.
#. In the search you can use:

   ``self.env['res.partner'].search([('name', '%', 'Jon Miller)])``

#. In this example the function will return positive result for `John Miller` or
   `John Mill`.

#. You can tweak the number of strings to be returned by adjusting the set limit
   (default: 0.3). NB: Currently you have to set the limit by executing the
   following SQL statment:

   ``self.env.cr.execute("SELECT set_limit(0.2);")``

#. Another interesting feature is the use of ``similarity(column, 'text')``
   function in the ``order`` parameter to order by similarity. This module just
   contains a basic implementation which doesn't perform validations and has to
   start with this function. For example you can define the function as
   followed:

   ``similarity(%s.name, 'John Mil') DESC" % self.env['res.partner']._table``

For further questions read the Documentation of the
`pg_trgm <https://www.postgresql.org/docs/current/static/pgtrgm.html>`_ module.


Known issues / Roadmap
======================

* Modify the general search parts (e.g. in tree view or many2one fields)
* add better `order by` handling


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

* Christoph Giesel <https://github.com/christophlsa>

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
