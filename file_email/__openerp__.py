# coding: utf-8
#   @author Sébastien BEAU @ Akretion
#   @author Florian DA COSTA @ Akretion
#   @author Benoit GUILLOT @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'File Email',
    'version': '9.0.1.0.0',
    'author': 'Akretion,Odoo Community Association (OCA)',
    'category': 'Generic Modules',
    'license': 'AGPL-3',
    'website': 'http://www.akretion.com/',
    'depends': [
        'attachment_base_synchronize',
        'fetchmail'
    ],
    'data': [
        'security/ir.model.access.csv',
        "views/fetchmail_view.xml",
        "views/attachment_view.xml",
    ],
    'demo': [],
    'installable': True,
    'images': [],
}
