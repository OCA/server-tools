# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Base Sequence Option",
    "summary": "Alternative sequence options for specific models",
    "version": "14.0.1.0.0",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "maintainers": ["kittiu"],
    "development_status": "Alpha",
    "website": "https://github.com/OCA/server-tools",
    "category": "Tools",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "security/sequence_option_security.xml",
        "views/sequence_option_view.xml",
    ],
    "license": "LGPL-3",
    "installable": True,
}
