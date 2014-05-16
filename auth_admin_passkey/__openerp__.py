# -*- encoding: utf-8 -*-
##############################################################################
#
#    Admin Passkey module for OpenERP
#    Copyright (C) 2013-2014 GRAP (http://www.grap.coop)
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
    'name': 'Authentification - Admin Passkey',
    'version': '2.1.1',
    'category': 'base',
    'description': """
Admin password become a passkey for all active logins
=====================================================

Functionality :
---------------
    * Administrator has now the possibility to login in with any login;
    * By default, OpenERP will send a mail to user and admin to indicate them;
    * If a user and the admin have the same password, admin will be informed;

Technical information :
-----------------------
    * Create two ir_config_parameter to enable / disable mail sending;

Copyright, Author and Licence :
-------------------------------
    * Copyright : 2014, Groupement Régional Alimentaire de Proximité;
    * Author : Sylvain LE GAL (https://twitter.com/legalsylvain);
    * Licence : AGPL-3 (http://www.gnu.org/licenses/)
    """,
    'author': 'GRAP',
    'website': 'http://www.grap.coop',
    'license': 'AGPL-3',
    'depends': [
        'mail',
        ],
    'data': [
        'data/ir_config_parameter.xml',
        'view/res_config_view.xml',
    ],
    'demo': [],
    'js': [],
    'css': [],
    'qweb': [],
    'images': [],
    'post_load': '',
    'application': False,
    'installable': True,
    'auto_install': False,
}
