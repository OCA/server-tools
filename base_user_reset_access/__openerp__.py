# -*- coding: utf-8 -*-
# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': "Base User Reset Access",
    'summary': """Reset User Access Right""",
    'author': "ACSONE SA/NV,Odoo Community Association (OCA)",
    'website': "http://acsone.eu",
    'category': 'Tools',
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'base',
    ],
    'data': [
        'views/res_users_view.xml',
    ],
    "installable": True,
}
