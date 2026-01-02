# Copyright 2026 Opener B.V. <https://opener.amsterdam>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError

from odoo.addons.base.tests.common import BaseCommon


class TestModelAuditlogRule(BaseCommon):
    def test_model_required(self):
        """Model is required, but not as a field property."""
        model_id = self.env.ref("base.model_res_groups").id
        # Test create
        with self.assertRaisesRegex(
            UserError,
            "No model defined to create line",
        ):
            with self.env.cr.savepoint():
                self.env["auditlog.rule"].create(
                    {
                        "name": "Test rule",
                    },
                )
        rule = self.env["auditlog.rule"].create(
            {
                "name": "Test rule",
                "model_id": model_id,
            },
        )
        # Test write
        with self.assertRaisesRegex(
            UserError,
            "'model_id' cannot be empty",
        ):
            with self.env.cr.savepoint():
                rule.model_id = False
