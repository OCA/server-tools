# Copyright 2017-2018 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# Raphaël Reverdy <raphael.reverdy@akretion.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Base JSONify",
    "summary": """
    Base module that provide the jsonify method on all models.

    WARNING: since version 14.0.2.0.0 the module have been renamed to `jsonifier`.
    This module now depends on it only for backward compatibility.
    It will be discarded in v15 likely.
    """,
    "version": "14.0.2.0.0",
    "category": "Uncategorized",
    "website": "https://github.com/OCA/server-tools",
    "author": "Akretion, ACSONE, Camptocamp, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "installable": True,
    "depends": ["jsonifier"],
}
