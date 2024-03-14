# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Base Force Record NOUPDATE",
    "summary": """
        Force noupdate=True for selected models """,
    "author": "Camtocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools",
    "category": "Hidden/Dependency",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["base_setup"],
    "data": ["views/res_config_settings_views.xml"],
    "installable": True,
}
