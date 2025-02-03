# Copyright 2022 Moka Tourisme (https://www.mokatourisme.fr).
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest import mock

from odoo.tests import TransactionCase


class IapAccountCase(TransactionCase):
    def setUp(self):
        super().setUp()
        self.service = self.env["iap.service"].create(
            {
                "name": "Some Service",
                "technical_name": "some-service",
                "description": "Test service",
                "unit_name": "unit",
                "integer_balance": 0,
            }
        )

    def test_create_odoo_iap(self):
        account = self.env["iap.account"].create(
            {
                "name": "Odoo IAP",
                "service_id": self.service.id,
            }
        )
        self.assertEqual(account.service_id.id, self.service.id)

    def test_create_with_mock(self):
        with mock.patch(
            "odoo.addons.iap_alternative_provider.models."
            "iap_account.IapAccount._get_service_from_provider",
            return_value="other-service",
        ):
            account = self.env["iap.account"].create(
                {
                    "name": "Odoo IAP",
                    "service_id": self.service.id,
                }
            )
            self.assertEqual(account.service_id.id, self.service.id)

    def test_write_odoo_iap(self):
        account = self.env["iap.account"].create(
            {
                "name": "Odoo IAP",
                "service_id": self.service.id,
            }
        )
        self.assertEqual(account.service_id.id, self.service.id)
        new_service = self.env["iap.service"].create(
            {
                "name": "New Service",
                "technical_name": "new-service",
                "description": "Another service",
                "unit_name": "new_unit",
                "integer_balance": 0,
            }
        )
        account.write({"service_id": new_service.id})
        self.assertEqual(account.service_id.id, new_service.id)
