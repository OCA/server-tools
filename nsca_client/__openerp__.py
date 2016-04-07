# -*- coding: utf-8 -*-
# © 2015 ABF OSIELL <http://osiell.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "NSCA Client",
    "summary": "Send passive alerts to monitor your Odoo application.",
    "version": "8.0.1.0.0",
    "category": "Tools",
    "website": "http://osiell.com/",
    "author": "ABF OSIELL, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "data": [
        "security/ir.model.access.csv",
        "data/nsca_server.xml",
        "views/nsca_menu.xml",
        "views/nsca_check.xml",
        "views/nsca_server.xml",
    ],
    "demo": [
        "demo/demo_data.xml",
    ],
}
