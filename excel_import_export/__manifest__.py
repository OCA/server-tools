# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    'name': 'Excel Import/Export',
    'summary': 'Base module for easy way to develop Excel import/export',
    'version': '12.0.1.0.1',
    'author': 'Ecosoft,Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'website': 'https://github.com/OCA/server-tools/',
    'category': 'Tools',
    'depends': ['mail'],
    'external_dependencies': {
        'python': [
            'xlrd',
            'xlwt',
            'openpyxl',
        ],
    },
    'data': ['security/ir.model.access.csv',
             'wizard/export_xlsx_wizard.xml',
             'wizard/import_xlsx_wizard.xml',
             'views/xlsx_template_view.xml',
             'views/xlsx_report.xml',
             ],
    'installable': True,
    'development_status': 'alpha',
    'maintainers': ['kittiu'],
}
