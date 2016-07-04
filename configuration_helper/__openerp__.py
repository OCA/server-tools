# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: David BEAL
#    Copyright 2014 Akretion
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
    'name': 'Configuration Helper',
    'version': '0.8',
    'author': "Akretion,Odoo Community Association (OCA)",
    'maintainer': 'Akretion',
    'category': 'server',
    'complexity': 'normal',
    'depends': ['base'],
    'description': """
Configuration Helper
====================

*This module is intended for developer only. It does nothing used alone.*

This module :

  * create automatically related fields in 'whatiwant.config.settings'
    using those defined in 'res.company' : it avoid duplicated field definitions.
  * company_id field with default value is created
  * onchange_company_id is defined to update all related fields
  * supported fields: char, text, integer, float, datetime, date, boolean, m2o


How to use
----------

.. code-block:: python

    from . company import ResCompany

    class WhatiwantClassSettings(orm.TransientModel):
        _inherit = ['res.config.settings', 'abstract.config.settings']
        _name = 'whatiwant.config.settings'
        # fields must be defined in ResCompany class
        # related fields are automatically generated from previous definitions
        _companyObject = ResCompany


Roadmap
-------
  * support (or check support) for these field types : o2m, m2m, reference, property, selection
  * automatically generate a default view for 'whatiwant.config.settings' (in --debug ?)


Contributors
------------

* David BEAL <david.beal@akretion.com>
* Sébastien BEAU <sebastien.beau@akretion.com>
* Yannick Vaucher, Camptocamp, (code refactoring from his module 'delivery_carrier_label_postlogistics')

 """,
    'website': 'http://www.akretion.com/',
    'data': [
    ],
    'tests': [],
    'installable': False,
    'auto_install': False,
    'license': 'AGPL-3',
    'application': True,
}
