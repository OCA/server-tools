# Copyright 2015-2017 Camptocamp SA
# Copyright 2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Track record changesets",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
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
        "views/record_changeset_views.xml",
        "views/record_changeset_change_views.xml",
        "views/changeset_field_rule_views.xml",
        "views/menu.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "base_changeset/static/src/components/form_label.*",
            "base_changeset/static/src/components/changeset_popover.*",
            "base_changeset/static/src/components/record.esm.js",
        ],
    },
    "demo": ["demo/changeset_field_rule.xml"],
    "installable": True,
}
