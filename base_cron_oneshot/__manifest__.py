# Copyright (C) 2018 by Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': """Single use crons""",
    'summary': """Allows creating of single-use disposable crons""",
    'category': "Extra Tools",
    'version': "11.0.1.0.0",

    'author': "Camptocamp SA, "
              "Odoo Community Association (OCA)",
    'website': "https://github.com/OCA/server-tools",
    'license': "AGPL-3",

    'data': [
        'views/ir_cron.xml',
        'data/ir_sequence.xml',
    ],
}
