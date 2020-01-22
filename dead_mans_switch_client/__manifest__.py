# © 2015-2016 Therp BV <http://therp.nl>
# © 2017 Avoin.Systems - Miku Laitinen
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Dead man's switch (client)",
    "version": "13.0.1.0.0",
    "author": "Therp BV, Avoin.Systems, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Monitoring",
    "summary": "Be notified when customers' Odoo instances go down",
    "description": """
    This module is the client part of `dead_mans_switch_server`. It is responsible
    of sending the server status updates, which in turn takes action if those
    updates don't come in time.
    """,
    "depends": ["base"],
    "data": ["data/ir_actions.xml", "data/ir_cron.xml", "views/ir_filters_views.xml"],
    "demo": ["data/client_demo.xml"],
    "installable": True,
}
