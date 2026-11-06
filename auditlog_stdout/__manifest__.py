# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Auditlog - option to log to STDOUT",
    "version": "18.0.1.0.0",
    "author": "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools",
    "license": "AGPL-3",
    "category": "Tools",
    "summary": "Allows to extend an auditlog rule to output to STDOUT.",
    "depends": [
        "auditlog",
    ],
    "data": [
        "views/auditlog_rule_view.xml",
    ],
    "installable": True,
}
