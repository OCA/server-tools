# Copyright 2026 Ledo Enterprises
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Fetchmail S3",
    "version": "18.0.1.0.0",
    "category": "Hidden/Tools",
    "summary": "Receive incoming emails from an S3-compatible bucket",
    "author": "Ledo Enterprises, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools",
    "license": "AGPL-3",
    "depends": ["mail"],
    "external_dependencies": {
        "python": ["boto3"],
    },
    "data": [
        "views/fetchmail_server_views.xml",
    ],
    "installable": True,
}
