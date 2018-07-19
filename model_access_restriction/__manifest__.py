# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Model access restriction',
    'summary': 'Restrict CRUD actions of specific models to some groups',
    'version': '10.0.1.0.0',
    'depends': [
        'base',
    ],
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'http://www.acsone.eu',
    'license': 'AGPL-3',
    'category': 'Security',
    'data': [
        'views/access_restriction.xml',
        'security/access_restriction.xml',
    ],
    'application': True,
}
