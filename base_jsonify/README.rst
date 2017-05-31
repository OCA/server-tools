.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==============
Base Jsonify
==============

This module add the jsonify method to the ORM. This method take as argument
the browse record and the "parser" that specify the field to extract.

Example of parser:


.. code-block:: python

    parser = [
        'name',
        'number',
        'create_date',
        ('partner_id', ['id', 'display_name', 'ref'])
        ('line_id', ['id', ('product_id', ['name']), 'price_unit'])
    ]

In order to be consitent with the odoo api the jsonify method always
return a list of object even if there is only one element in input

By default the key into the json is the name of the field extracted
from the model. If you need to specify an alternate name to use as key, you
can definne your mapping as follow into the parser definition:

.. code-block:: python

    parser = [
         'field_name:json_key'
    ]

.. code-block:: python


    parser = [
        'name',
        'number',
        'create_date:creationDate',
        ('partner_id:partners', ['id', 'display_name', 'ref'])
        ('line_id:lines', ['id', ('product_id', ['name']), 'price_unit'])
    ]

Also the module provide a method "get_json_parser" on the ir.exports object
that generate a parser from an ir.exports configuration



Installation
============

To install this module, you need to install it

Configuration
=============

No configuration required

Usage
=====

This is a technical module not function feature is added

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/{repo_id}/{branch}

.. repo_id is available in https://github.com/OCA/maintainer-tools/blob/master/tools/repos_with_ids.txt
.. branch is "8.0" for example

Known issues / Roadmap
======================

Nothing yet

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/{project_repo}/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* BEAU Sébastien <sebastien.beau@akretion.com>
* Laurent Mignon <laurent.mignon@acsone.eu>

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
