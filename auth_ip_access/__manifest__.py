# coding: utf-8
# Copyright 2020 Stefan Rijnhart <stefan@opener.amsterdam>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "IP level access restriction",
    "summary": "Apply IP access restriction policies per user group",
    "version": "10.0.1.0.0",
    "development_status": "Beta",
    "category": "Security",
    "website": "https://github.com/OCA/server-tools",
    "author": "Opener B.V., Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "preloadable": True,
    # Note: install package as py2-ipaddress
    "external_dependencies": {"python": ['ipaddress'], },
    "depends": [
        # auth_crypt overwrites methods we override
        "auth_crypt",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/ip_access_rule.xml",
    ],
}
