# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Safe Translations Check",
    "description": """Check all database translations for errors.""",
    "version": "12.0.1.0.0",
    "depends": ["base_safe_translations", "queue_job"],
    "author": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    "license": "AGPL-3",
    "category": "Localization",
    "data": ["wizard/ir_translation_safe_wizard.xml"],
    "demo": [],
    "installable": True,
}
