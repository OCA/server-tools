# coding: utf-8
# @ 2015 Valentin CHEMIERE @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{'name': 'attachment_metadata',
 'version': '0.0.1',
 'author': 'Akretion',
 'website': 'www.akretion.com',
 'license': 'AGPL-3',
 'category': 'Generic Modules',
 'description': """
 Add some useful field to ir.attachment object like:
 internal and external hash for coherence verification
 """,
 'depends': [
     'base',
     'mail'
 ],
 'data': [
     'attachment_view.xml',
     'security/ir.model.access.csv',
 ],
 'installable': True,
 'application': False,
 }
