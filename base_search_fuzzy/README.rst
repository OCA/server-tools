.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=========================
PostgreSQL Trigram Search
=========================

This addon provides the ability to create GIN or GiST indexes of char and text
fields and also to use the search operator `%` in search domains. Currently
this module doesn't change the backend search or anything else. It provides
only the possibilty to perfrom the fuzzy search for external addons.


Installation
============

#. The PostgreSQL extension ``pg_trgm`` should be available. In debian based
   distribution you have to install the `postgresql-contrib` module.
#. Install the ``pg_trgm`` extension to your database or give your postgresql
   user the ``SUPERUSER`` right (this allows the odoo module to install the
   extension to the database).


Configuration
=============

If the odoo module is installed:

#. You can define ``GIN`` and ``GiST`` indexes for `char` and `text` via
   `Settings -> Database Structure -> Trigram Index`. The index name will
   automatically created for new entries.


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
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Christoph Giesel <https://github.com/christophlsa>
* Jordi Ballester <jordi.ballester@eficent.com>
* Serpent Consulting Services Pvt. Ltd. <support@serpentcs.com>
* Dave Lasley <dave@laslabs.com>

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
