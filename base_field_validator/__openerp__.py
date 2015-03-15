# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Agile Business Group sagl (<http://www.agilebg.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': "Fields Validator",
    'version': '0.1',
    'category': 'Tools',
    'summary': "Validate fields using regular expressions",
    'description': """
Fields Validator
================

This module allows to set a regular expression as field validator.
When the regular expresion is set, write and create operations on the involved
field are blocked, if the regular expression is not satisfied.
See demo and test data for an example with partner email.


Configuration
=============

Open ir.model form (say res.partner) and add 'Validators' lines


Known issues / Roadmap
======================

The module performs the check at server side. Client side check is also needed,
to improve user experience and avoid server calls when unnecessary


Credits
=======

Contributors
------------

* Lorenzo Battistini <lorenzo.battistini@agilebg.com>
* Nicola Malcontenti <nicola.malcontenti@agilebg.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization
whose mission is to support the collaborative development of Odoo features
and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.

""",
    'author': 'Agile Business Group',
    'website': 'http://www.agilebg.com',
    'license': 'AGPL-3',
    "depends": ['base'],
    "data": [
        'ir_model_view.xml',
        'security/ir.model.access.csv',
        ],
    "demo": [
        'ir_model_demo.xml',
        ],
    'test': [
        'test/validator.yml',
    ],
    "active": False,
    "installable": True
}
