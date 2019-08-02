# Copyright 2019 Digital5 S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Record Merge',
    'summary': """
        Merges any number of records from any table""",
    'version': '11.0.0.0.1',
    'license': 'AGPL-3',
    'author': 'Digital5 S.L.,Odoo Community Association (OCA)',
    'depends': [
        'base',
    ],
    'data': [
        #'security/record_merge_id.xml',
        'views/record_merge_id.xml',
        #'security/record_merge_criteria.xml',
        'views/record_merge_criteria.xml',
    ],
    'demo': [
    ],
}
