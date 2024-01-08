# Copyright - 2013-2024 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Email gateway - folders",
    "summary": "Attach mails in an IMAP folder to existing objects",
    "version": "16.0.1.1.0",
    "author": "Therp BV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools",
    "license": "AGPL-3",
    "category": "Tools",
    "depends": ["mail"],
    "data": [
        "views/fetchmail_server.xml",
        "wizard/attach_mail_manually.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "auto_install": False,
}
