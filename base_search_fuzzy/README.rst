.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=========================
PostgreSQL Trigram Search
=========================

This addon provides the ability to create GIN or GiST indexes of char and text
fields and also to use the search operator `%` in search domains. Currently
this module doesn't change the backend search or something else. It provides
only the possibilty to do a fuzzy search for external addons.


Installation
============

First you need to have the ``pg_trgm`` extension available. In debian based
distribution you have to install the `postgresql-contrib` module. Then you have
to either install the ``pg_trgm`` extension to your database or you have to give
your postgresql user the superadmin right (this allows the odoo module to
install the extension to the database).


Configuration
=============

If you installed the odoo module you can define ``GIN`` and ``GiST`` indexes for
`char` and `text` via `Settings -> Database Structure -> Trigram Index`. The
index name will automatically created for new entries.


Usage
=====

For example you can create an index for the `name` field of `res.partner`. Then
in a search you can use

``self.env['res.partner'].search([('name', '%', 'Jon Miller)])``

In this Example it can find existing names like `John Miller` or `John Mill`.

Which strings can be found depends on the limit which is set (default: 0.3).
Currently you have to set the limit by executing SQL:

``self.env.cr.execute("SELECT set_limit(0.2);")``

Also you can use the ``similarity(column, 'text')`` function in the ``order``
parameter to order by the similarity. This is just a basic implementation which
doesn't contains validations and has to start with this function. For example
you can define this like:

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
