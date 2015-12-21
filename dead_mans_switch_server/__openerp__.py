# -*- coding: utf-8 -*-
# © 2015 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Dead man's switch (server)",
    "version": "8.0.1.0.0",
    "author": "Therp BV,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Monitoring",
    "summary": "Be notified when customers' odoo instances go down",
    "depends": [
        'mail',
        'web_kanban_sparkline',
    ],
    "data": [
        "data/ir_cron.xml",
        "security/res_groups.xml",
        "views/dead_mans_switch_log.xml",
        "views/dead_mans_switch_instance.xml",
        "views/menu.xml",
        'security/ir.model.access.csv',
    ],
}
