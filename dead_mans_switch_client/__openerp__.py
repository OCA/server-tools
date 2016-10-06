# -*- coding: utf-8 -*-
# © 2015-2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Dead man's switch (client)",
    "version": "9.0.1.0.1",
    "author": "Therp BV,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Monitoring",
    "summary": "Be notified when customers' odoo instances go down",
    "depends": [
        'base',
    ],
    "data": [
        "data/ir_actions.xml",
        "data/ir_cron.xml",
    ],
    "demo": [
        "demo/dead_mans_switch_client_demo.yml",
    ],
    'installable': False,
}
