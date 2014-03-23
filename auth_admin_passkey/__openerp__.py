# -*- encoding: utf-8 -*-
################################################################################
#    See Copyright and Licence Informations undermentioned.
################################################################################

{
    'name': 'Authentification - Admin Passkey',
    'version': '2.1',
    'category': 'base',
    'description': """
Admin password become a passkey for all active logins
=====================================================

Functionnality :
----------------
    * Administrator has now the possibility to login in with any login;
    * By default, OpenERP will send a mail to user and admin to indicate them;
    * If a user has the same password as the admin, OpenERP will inform the admin;

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
