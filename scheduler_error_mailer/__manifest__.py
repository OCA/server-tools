# Copyright 2012-2013 Akretion Sébastien BEAU,David Beal,Alexis de Lattre
# Copyright 2016 Sodexis
# Copyright 2018 bloopark systems (<http://bloopark.de>)
# Copyright 2019 Tecnativa - Cristina Martin R.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Scheduler Error Mailer",
    "version": "13.0.1.0.0",
    "category": "Extra Tools",
    "license": "AGPL-3",
    "author": "Akretion,Sodexis,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools",
    "depends": ["mail"],
    "data": ["data/ir_cron_email_tpl.xml", "views/ir_cron.xml"],
    "demo": ["demo/ir_cron_demo.xml"],
    "images": ["images/scheduler_error_mailer.jpg"],
    "installable": True,
}
