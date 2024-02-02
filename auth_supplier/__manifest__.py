# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Sergio Teruel
# (c) 2015 Antiun Ingeniería S.L. - Carlos Dauden
# © 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': "Auth Supplier",
    'category': 'Portal',
    'version': '10.0.1.0.0',
    'depends': [
        'auth_signup',
    ],
    'data': [
        'views/auth_supplier_view.xml',
    ],
    'author': 'Antiun Ingeniería S.L., '
              'Incaser Informatica S.L., '
              "Tecnativa, "
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/server-tools'
               '/tree/10.0/auth_supplier',
    'license': 'AGPL-3',
    'installable': True,
}
