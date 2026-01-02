# Copyright 2026 Opener B.V. <https://opener.amsterdam>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError

from odoo.addons.base.tests.common import BaseCommon


class TestModelAuditlogLog(BaseCommon):
    def test_field_required(self):
        """Model and field are required on log/line, but not as a field property."""
        model_id = self.env.ref("base.model_res_groups").id
        field_id = self.env.ref("base.field_res_groups__name").id
        # Test log create
        with self.assertRaisesRegex(
            UserError,
            "No model defined to create log",
        ):
            with self.env.cr.savepoint():
                self.env["auditlog.log"].create({})
        log = self.env["auditlog.log"].create(
            {
                "model_id": model_id,
            },
        )
        self.assertEqual(log.model_model, "res.groups")
        # Test log write
        with self.assertRaisesRegex(
            UserError,
            "'model_id' cannot be empty",
        ):
            with self.env.cr.savepoint():
                log.model_id = False

        # Test line create
        with self.assertRaisesRegex(
            UserError,
            "No field defined to create line",
        ):
            with self.env.cr.savepoint():
                line = self.env["auditlog.log.line"].create(
                    {
                        "log_id": log.id,
                    },
                )
        line = self.env["auditlog.log.line"].create(
            {
                "log_id": log.id,
                "field_id": field_id,
            },
        )
        # Test line write
        with self.assertRaisesRegex(
            UserError,
            "'field_id' cannot be empty",
        ):
            with self.env.cr.savepoint():
                line.field_id = False
