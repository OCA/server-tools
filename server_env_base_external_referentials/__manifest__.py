# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2011-2012 Camptocamp SA
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
    "name": "Server environment for base_external_referential",
    "version": "1.0",
    "depends": ["base", 'server_environment', 'base_external_referentials'],
    "author": "Camptocamp,Odoo Community Association (OCA)",
    'license': 'AGPL-3',
    "description": """This module is based on the server_environment module to use files for configuration.
Thus we can have a different file for each environment (dev, test, staging, prod).
This module define the config variables for the base_external_referential module.
In the configuration file, you can configure the url, login and password of the referentials

Exemple of the section to put in the configuration file :

[external_referential.name_of_my_external_referential]
location = http://localhost/magento/
apiusername = my_api_login
apipass = my_api_password
    """,
    "website": "https://github.com/OCA/server-tools",
    "category": "Tools",
    "init_xml": [],
    "demo_xml": [],
    "update_xml": [],
    "installable": False,
    "active": False,
}
