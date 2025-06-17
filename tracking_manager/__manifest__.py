# Copyright 2022 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Tracking Manager",
    "summary": """This module tracks all fields of a model,
                including one2many and many2many ones.""",
    "version": "18.0.1.1.0",
    "category": "Tools",
    "website": "https://github.com/OCA/server-tools",
    "author": "Akretion, Odoo Community Association (OCA)",
    "maintainers": ["Kev-Roche", "sebastienbeau"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["mail"],
    "data": [
        "views/ir_model_fields.xml",
        "views/ir_model.xml",
        "views/message_template.xml",
    ],
}
