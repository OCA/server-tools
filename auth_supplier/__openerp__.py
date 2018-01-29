# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Sergio Teruel
# (c) 2015 Antiun Ingeniería S.L. - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': "Auth Supplier",
    'category': 'Tools',
    'version': '8.0.1.0.0',
    'depends': [
        'auth_signup',
    ],
    'data': [
        'security/auth_supplier_security.xml',
        'views/auth_supplier_view.xml',
    ],
    'author': 'Antiun Ingeniería S.L., '
              'Incaser Informatica S.L., '
              'Odoo Community Association (OCA)',
    'website': 'http://www.incaser.es',
    'license': 'AGPL-3',
    'installable': False,
}
