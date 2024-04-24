# © 2015 ABF OSIELL <http://osiell.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "NSCA Client",
    "summary": "Send passive alerts to monitor your Odoo application.",
    "version": "16.0.1.0.0",
    "category": "Tools",
    "website": "https://github.com/OCA/server-tools",
    "author": "ABF OSIELL, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/nsca_menu.xml",
        "views/nsca_check.xml",
        "views/nsca_server.xml",
    ],
    "external_dependencies": {"deb": ["nsca-client"]},
    "demo": ["demo/demo_data.xml"],
}
