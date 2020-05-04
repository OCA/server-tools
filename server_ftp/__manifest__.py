# Copyright 2020 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Server FTP",
    "version": "13.0.1.0.0",
    "author": "Therp BV, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools",
    "license": "AGPL-3",
    "category": "Tools",
    "summary": "Enable connection via various protocols",
    "depends": ["base"],
    "data": ["security/ir.model.access.csv", "views/server_ftp_views.xml"],
    "demo": ["demo/server_ftp.xml", "demo/server_ftp_folder.xml"],
    "external_dependencies": {"python": ["pysftp"]},
    "installable": True,
}
