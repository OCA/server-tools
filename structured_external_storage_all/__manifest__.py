# -*- coding: utf-8 -*-
# © 2018 Sunflower IT (http://sunflowerweb.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Structured External Storage All Attachments",
    "version": "11.0.1.0.0",
    "category": "Storage",
    "author": "Sunflower IT,Odoo Community Association (OCA)",
    "website": "https://sunflowerweb.nl",
    "license": "AGPL-3",
    "summary": "Define Folder Structure for Attachments to Sync",
    "depends": [
        "external_file_location",
    ],
    "data": [
        "security/res_groups.xml",
        "views/views.xml",
        "views/res_request_link.xml",
        "views/ir_attachment_metadata.xml",
        "wizard/attachment_sync_rule_all.xml",
        "wizard/attachment_sync_create_metas_all.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
}
