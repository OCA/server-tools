# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


{'name': 'Excel Import/Export',
 'version': '11.0.0.0.0',
 'author': 'Ecosoft,Odoo Community Association (OCA)',
 'license': 'AGPL-3',
 'category': 'Generic Modules',
 'depends': ['mail'],
 'external_dependencies': {
    'python': ['unicodecsv', 'xlrd', 'xlwt', 'openpyxl'], },
 'data': ['wizard/export_xlsx_wizard.xml',
          'wizard/import_xlsx_wizard.xml',
          'views/xlsx_template_view.xml',
          'views/xlsx_report.xml',
          ],
 'installable': True,
 'development_status': '????',
 'maintainers': ['kittiu'],
 }
