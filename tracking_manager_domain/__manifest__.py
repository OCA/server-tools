# Copyright 2025 glueckkanja AG (<https://www.glueckkanja.com>) - Christopher Rogos
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Tracking Manager Domain",
    "summary": "This module extends the tracking manager to"
    " allow to define a domain on fields to track changes "
    "only when certain conditions apply.",
    "version": "18.0.1.0.1",
    "category": "Tools",
    "website": "https://github.com/OCA/server-tools",
    "author": "glueckkanja AG, Odoo Community Association (OCA)",
    "maintainers": ["CRogos"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["tracking_manager"],
    "data": [
        "views/ir_model_fields.xml",
    ],
}
