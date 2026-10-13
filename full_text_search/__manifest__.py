# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Full Text Search",
    "summary": "Adds full text search capabilities to Odoo",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "category": "Tools",
    "website": "https://github.com/OCA/server-tools",
    "author": "Akretion, Odoo Community Association (OCA)",
    "depends": ["web"],
    "data": ["views/assets.xml"],
    "maintainers": ["paradoxxxzero"],
    "installable": True,
    "post_load": "post_load",
}
