# -*- encoding: utf-8 -*-
##############################################################################
#
#    Authentification - Generate Password module for Odoo
#    Copyright (C) 2014 GRAP (http://www.grap.coop)
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
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
    'name': 'Authentification - Generate Password',
    'version': '7.0.1.0.1',
    'category': 'Tools',
    'description': """
Password Secure
===============

Functionnality:
---------------
* Forbid users to change them password;
    * Only members of base.group_system can change password; OK.
* Add a button to the res_users form:
    * to change the password (randomly generated);
    * send an email to each users;

Settings:
---------
* Once the module installed, you have to set two settings:
    * password size: the size of the password generated (6 by default);
    * password chars: the list of allowed chars (by default ASCII letters
      and digits); You can:
        * set a list of chars like 'abcdef';
        * use string function like string.ascii_letters;
* Be sure that an Outgoing Email Server is correctly configured;

Roadmap
-------
* When porting this module, please remove the feature that forbid users to
  change them password, as another module 'password_change_restrict' exists in
  V8 serie : https://github.com/OCA/server-tools/pull/249

Copyright, Author and Licence :
-------------------------------
    * Copyright : 2014, Groupement Regional Alimentaire de Proximite;
    * Author : Sylvain LE GAL (https://twitter.com/legalsylvain);
    * Licence : AGPL-3 (http://www.gnu.org/licenses/)
    """,
    'author': 'GRAP',
    'website': 'http://www.grap.coop',
    'license': 'AGPL-3',
    'depends': [
        'email_template',
    ],
    'data': [
        'data/ir_config_parameter.xml',
        'data/email_template.xml',
        'view/view.xml',
    ],
    'demo': [
        'demo/res_groups.yml',
        'demo/res_users.yml',
    ],
}
