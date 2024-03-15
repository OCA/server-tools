# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mass Mailing Mail Server",
    "summary": """
        You can give to all mail servers a minimum number of recipients.
        On a mass mailing, if you don't provide a mail server, Odoo will chose
        the first one for which the minimum number of recipients on it is
        less than or equal to the number of recipients of your mass mailing.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools",
    "depends": [
        "mass_mailing",
    ],
    "data": [
        "views/ir_mail_server.xml",
    ],
    "demo": [],
}
