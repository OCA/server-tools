# Copyright 2021 Ecosoft
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo.tests import common


class TestRequestRequest(common.TransactionCase):
    def setUp(self):
        super(TestRequestRequest, self).setUp()
        self.tier_definition = self.env["tier.definition"]

    def test_get_tier_validation_model_names(self):
        self.assertIn(
            "request.request",
            self.tier_definition._get_tier_validation_model_names(),
        )
