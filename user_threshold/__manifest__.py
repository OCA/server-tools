# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    "name": "User Threshold",
    "summary": "Add Configurable User Threshold Support",
    "version": "11.0.1.0.0",
    "category": "Authentication",
    "website": "https://github.com/OCA/server-tools",
    "author": "initOS GmbH, LasLabs, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "application": False,
    'installable': True,
    "data": [
        'data/user_threshold_data.xml',
        'data/ir_config_parameter_data.xml',
        'views/res_company_view.xml',
        'views/res_users_view.xml',
    ],
}
