# Copyright 2011 Raphaël Valyi, Renato Lima, Guewen Baconnier, Sodexis
# Copyright 2017 Akretion (http://www.akretion.com)
# Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': 'Exception Rule',
    'version': '12.0.2.0.3',
    'category': 'Generic Modules',
    'summary': """
    This module provide an abstract model to manage customizable
    exceptions to be applied on different models (sale order, invoice, ...)""",
    'author':
        "Akretion, Sodexis, Camptocamp, Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/server-tools',
    'depends': [
        'base_setup',
    ],
    'license': 'AGPL-3',
    'data': [
        'security/base_exception_security.xml',
        'security/ir.model.access.csv',
        'wizard/base_exception_confirm_view.xml',
        'views/base_exception_view.xml',
    ],
    'installable': True,
}
