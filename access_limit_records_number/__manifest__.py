# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": """Limit number of records""",
    "summary": """e.g. allow to create maximum 10 users. Similar restriction can be applied to any table.""",
    "category": "Extra tools",
    "version": "18.0.1.0.0",
    "author": "Ivan Yelizariev, Pavel Romanchenko, IT Projects Labs, Miguel Martinez Lopez, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/server-tools",
    "depends": ["base_automation"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/base_limit_records_number.xml",
    ],
    "installable": True,
    "auto_install": False,
}
