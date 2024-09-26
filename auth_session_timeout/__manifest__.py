# -*- coding: utf-8 -*-
# (c) 2015 ACSONE SA/NV, Dhinesh D
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': "Inactive Sessions Timeout",
    'summary': """
        This module disable all inactive sessions since a given delay""",
    'author': "ACSONE SA/NV, "
              "Dhinesh D, "
              "Jesse Morgan, "
              "LasLabs, "
              "Odoo Community Association (OCA)",
    'maintainer': 'Odoo Community Association (OCA)',
    'website': "https://github.com/OCA/server-tools"
               "/tree/10.0/auth_session_timeout",
    'category': 'Tools',
    'version': '10.0.1.0.3',
    'license': 'AGPL-3',
    'data': [
        'data/ir_config_parameter_data.xml'
    ],
    'installable': True,
}
