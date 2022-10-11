# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': "Base Technical User",
    'summary': """
        Add a technical user parameter on the company """,
    'author': 'ACSONE SA/NV, Odoo Community Association (OCA)',
    'website': "http://acsone.eu",
    'category': 'Hidden/Dependency',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'base',
    ],
    'data': [
        'views/res_company_view.xml'
    ],
    'installable': True
}
