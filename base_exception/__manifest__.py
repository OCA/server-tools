# -*- coding: utf-8 -*-
# © 2011 Raphaël Valyi, Renato Lima, Guewen Baconnier, Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{'name': 'Exception Rule',
 'version': '10.0.1.0.0',
 'category': 'Generic Modules',
 'summary': """This module provide an abstract model to manage customizable
  exceptions to be applied on different models (sale order, invoice, ...)""",
 'author': "Akretion, Sodexis, Camptocamp, Odoo Community Association (OCA)",
 'website': 'http://www.akretion.com',
 'depends': ['base_setup'],
 'license': 'AGPL-3',
 'data': [
     'security/base_exception_security.xml',
     'security/ir.model.access.csv',
     'wizard/base_exception_confirm_view.xml',
     'views/base_exception_view.xml',
 ],
 'installable': True,
 'pre_init_hook': 'pre_init_hook',
 }
