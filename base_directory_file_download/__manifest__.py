# Copyright 2017-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Directory Files Download",
    "summary": "Download all files of a directory on server",
    "author": "Onestein, Odoo Community Association (OCA)",
    "maintainers": ["astirpe"],
    "website": "https://github.com/OCA/server-tools",
    "category": "Tools",
    "version": "13.0.1.0.0",
    "development_status": "Production/Stable",
    "license": "AGPL-3",
    "depends": ["base_setup"],
    "data": [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "views/ir_filesystem_directory.xml",
    ],
    "installable": True,
}
