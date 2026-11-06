# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import Command
from odoo.tests.common import TransactionCase


class JsonifierCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ir_export_id = cls.env["ir.exports"].create(
            {
                "name": "Partner Export",
                "resource": "res.partner",
                "export_fields": [
                    Command.create({"name": name})
                    for name in (
                        "name",
                        "active",
                        "partner_latitude",
                        "color",
                        "category_id/name",
                        "country_id/name",
                        "country_id/code",
                        "child_ids/name",
                        "child_ids/id",
                        "child_ids/email",
                        "child_ids/country_id/name",
                        "child_ids/country_id/code",
                        "child_ids/child_ids/name",
                        "lang",
                        "comment",
                    )
                ],
            }
        )
