# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Resource Calendar Schedule Iteration",
    "author": "Eficent, Odoo Community Association (OCA)",
    "version": "11.0.1.0.0",
    'category': 'Hidden',
    "website": "https://github.com/OCA/server-tools",
    "depends": [
        'resource',
    ],
    "data": [
        'data/ir_config_parameter_data.xml',
    ],
    "license": 'LGPL-3',
    "post_load": "post_load_hook",
    "installable": True
}
