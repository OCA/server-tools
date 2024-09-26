# -*- coding: utf-8 -*-
# Copyright 2014 ABF OSIELL <http://osiell.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


{
    'name': 'User roles',
    'version': '10.0.1.0.3',
    'category': 'Tools',
    'author': 'ABF OSIELL, Odoo Community Association (OCA)',
    'license': 'LGPL-3',
    'maintainer': 'ABF OSIELL',
    'website': 'https://github.com/OCA/server-tools'
               '/tree/10.0/base_user_role',
    'depends': [
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_module_category.xml',
        'data/ir_cron.xml',
        'views/role.xml',
        'views/user.xml',
    ],
    'installable': True,
    'auto_install': False,
}
