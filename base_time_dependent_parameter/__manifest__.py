# Author Copyright (C) 2022 Nimarosa (Nicolas Rodriguez) (<nicolasrsande@gmail.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Time Dependent Parameter',
    'version': '14.0.1.0.0',
    'description': 'Allow defining time dependent parameters which can be used in another modules',
    'summary': 'Time dependent parameters adds the feature to define parameters with time based versions which can be consumed by another modules like Payroll.',
    'author': 'Nimarosa, OCA',
    'website': 'www.nimarosa.dev',
    "maintainers": ["appstogrow"],
    'license': 'LGPL-3',
    'category': 'Technical',
    'depends': [
        'base',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/base_time_parameter_views.xml',
    ],
    'installable': True,
}
