# -*- coding: utf-8 -*-
# © 2011 Raphaël Valyi, Renato Lima, Guewen Baconnier, Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{'name': 'Exception Rule',
 'version': '10.0.1.0.0',
 'category': 'Generic Modules/Sale',
 'author': "Akretion, Sodexis, Odoo Community Association (OCA)",
 'website': 'http://www.akretion.com',
 'depends': ['sale'],
 'license': 'AGPL-3',
 'data': [
     'security/base_exception_security.xml',
     'security/ir.model.access.csv',
     'wizard/base_exception_confirm_view.xml',
     'views/base_exception_view.xml',
 ],
 'installable': True,
 }
