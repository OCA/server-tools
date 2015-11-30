# -*- coding: utf-8 -*-
# © 2015 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Dead man's switch (client)",
    "version": "1.0.0",
    "author": "Therp BV,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Monitoring",
    "description": """
==========================
Dead man's switch (client)
==========================

This module is the client part of `dead_mans_switch_server`. It is responsible
of sending the server status updates, which in turn takes action if those
updates don't come in time.

Configuration
=============

After installing this module, you need to fill in the system parameter
`dead_mans_switch_client.url`. This must be the full URL to the server's
controller, usually of the form https://your.server/dead_mans_switch/alive

This module attempts to send CPU and RAM statistics to the server. While this
is not mandatory, it's helpful for assessing a server's health. If you want
this, you need to install `psutil`.

You can also have the currently online users logged, but this only works if
the `im_chat` module is installed.""",
    "depends": [
        'base',
    ],
    "data": [
        "data/ir_actions.xml",
        "data/ir_cron.xml",
    ],
}
