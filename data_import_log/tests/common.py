# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import base64

from odoo.tests import TransactionCase


class DataImportCase(TransactionCase):
    def _create_log(self, content=b"a,b\n1,2\n", file_name="feed.csv", **vals):
        attachment = self.env["ir.attachment"].create(
            {"name": file_name, "datas": base64.b64encode(content)}
        )
        log = self.env["data.import.log"]
        return log.create(
            dict(
                {
                    "attachment_id": attachment.id,
                    "content_hash": log._content_hash(content),
                },
                **vals,
            )
        )
