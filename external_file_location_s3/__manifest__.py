# -*- coding: utf-8 -*-
# © 2018 Sunflower IT (http://sunflowerweb.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "External File Location S3",
    "version": "11.0.1.0.0",
    "category": "Storage",
    "author": "Sunflower IT,Odoo Community Association (OCA)",
    "website": "https://sunflowerweb.nl",
    "license": "AGPL-3",
    "summary": "Sync Attachments to Amazon S3 Bucket",
    "depends": [
         "external_file_location",
    ],
    "data": [
        "data/sync_data.xml",
        "views/external_file_location.xml",
    ],
    "external_dependencies": {
        "python": [
            "boto3",
        ],
    },
    "installable": True,
}
