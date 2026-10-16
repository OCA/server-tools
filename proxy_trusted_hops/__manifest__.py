# Copyright 2026 Ametras intelligence GmbH
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Proxy Trusted Hops",
    "summary": "Configure how many reverse proxies Odoo trusts for the client IP",
    "version": "16.0.1.0.0",
    "category": "Tools",
    "author": "Ametras intelligence GmbH, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools",
    "license": "LGPL-3",
    "depends": ["base"],
    "post_load": "post_load",
    "installable": True,
}
