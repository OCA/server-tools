# Copyright (C) 2018 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': """Oneshot cron""",
    'summary': """Allows creating of single-use disposable crons.""",
    'category': "Extra Tools",
    'version': "11.0.1.0.0",
    'author': "Camptocamp, "
              "Odoo Community Association (OCA)",
    'website': "https://github.com/OCA/server-tools",
    'license': "AGPL-3",
    'data': [
        'data/ir_sequence.xml',
        'data/ir_cron.xml',
        'views/ir_cron.xml',
    ],
}
