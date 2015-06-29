# -*- encoding: utf-8 -*-
##############################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: moylop260@vauxoo.com
#    planned by: nhomar@vauxoo.com
#                moylop260@vauxoo.com
############################################################################
{
    'name': 'Webhook',
    'version': '1.1',
    'author': 'Vauxoo',
    'category': 'Server Tools',
    'website': 'https://www.vauxoo.com',
    'depends': [
        'web',
    ],
    'external_dependencies': {
        'python': ['ipaddress'],
    },
    'data': [
        'views/webhook_views.xml',
        'data/webhook_data.xml',
    ],
    'qweb': [
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
