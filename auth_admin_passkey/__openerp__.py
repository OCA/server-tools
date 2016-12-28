# -*- coding: utf-8 -*-
# Copyright 2013-2014 GRAP (http://www.grap.coop)
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# Copyright 2016 Serpent Consulting Services Pvt. Ltd. 
#                 (http://www.serpentcs.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Authentication - Admin Passkey',
    'version': '9.0.1.0.0',
    'category': 'base',
    'author': "GRAP, Odoo Community Association (OCA),"
            "Serpent Consulting Services Pvt. Ltd.",
                
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
    'auto_install': False,
}
