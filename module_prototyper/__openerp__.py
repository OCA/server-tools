# -*- coding: utf-8 -*-
# © 2010 - 2014 Savoir-faire Linux (<http://www.savoirfairelinux.com>)
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Module Prototyper',
    'version': '9.0.0.1.0',
    'author': 'Savoir-faire Linux,'
              'Sudokeys, '
              'ACSONE SA/NV,'
              'Odoo Community Association (OCA)',
    'maintainer': 'Savoir-faire Linux',
    'website': 'http://www.savoirfairelinux.com',
    'license': 'AGPL-3',
    'category': 'Others',
    'summary': 'Prototype your module.',
    'data': [
        'wizard/module_prototyper_module_export_view.xml',
        'views/module_prototyper_view.xml',
        'views/ir_model_fields_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
}
