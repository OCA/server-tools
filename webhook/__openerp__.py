# -*- coding: utf-8 -*-
##############################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    license: http://www.gnu.org/licenses/agpl-3.0.html
#    info Vauxoo (info@vauxoo.com)
#    coded by: moylop260@vauxoo.com
#    planned by: nhomar@vauxoo.com
#                moylop260@vauxoo.com
############################################################################
{
    'name': 'Webhook',
    'version': '1.1',
    'author': 'Vauxoo, Odoo Community Association (OCA)',
    'category': 'Server Tools',
    'website': 'https://www.vauxoo.com',
    'license': 'AGPL-3',
    'depends': [
        'web',
    ],
    'external_dependencies': {
        'python': [
            'ipaddress',
            'requests',
        ],
    },
    'data': [
        'views/webhook_views.xml',
        'data/webhook_data.xml',
    ],
    'qweb': [
    ],
    'demo': [
        'demo/webhook_demo.xml',
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
