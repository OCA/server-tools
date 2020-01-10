# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Base Cron Exclusion",
    "summary": "Allow you to select scheduled actions that should not run "
               "simultaneously.",
    "version": "12.0.1.0.0",
    "author": "Eficent, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools",
    "category": "Tools",
    "depends": [
        "base",
    ],
    "data": [
        "views/ir_cron_view.xml",
    ],
    "license": "LGPL-3",
    "installable": True,
}
