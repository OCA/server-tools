# Copyright 2015-2017 Camptocamp SA
# Copyright 2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Track record changesets",
    "version": "14.0.2.0.2",
    "development_status": "Beta",
    "author": "Onestein, Camptocamp, Odoo Community Association (OCA)",
    "maintainers": ["astirpe"],
    "license": "AGPL-3",
    "category": "Tools",
    "depends": ["web"],
    "website": "https://github.com/OCA/server-tools",
    "data": [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "security/rules.xml",
        "templates/assets.xml",
        "views/record_changeset_views.xml",
        "views/record_changeset_change_views.xml",
        "views/changeset_field_rule_views.xml",
        "views/menu.xml",
    ],
    "demo": ["demo/changeset_field_rule.xml"],
    "qweb": ["static/src/xml/backend.xml"],
    "installable": True,
}
