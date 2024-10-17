# Copyright 2023 Tecnativa - Víctor Martínez
# Copyright 2023 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Base Changeset Tier Validation",
    "version": "14.0.1.0.0",
    "category": "Tools",
    "website": "https://github.com/OCA/server-tools",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["base_changeset", "base_tier_validation"],
    "data": [
        "views/assets_backend.xml",
        "views/changeset_field_rule_views.xml",
        "views/record_changeset_views.xml",
        "views/record_changeset_views.xml",
        "views/tier_definition_views.xml",
        "views/tier_review_views.xml",
        "templates/tier_validation_templates.xml",
    ],
    "qweb": ["static/src/xml/tier_review_template.xml"],
    "installable": True,
    "maintainers": ["victoralmau"],
}
