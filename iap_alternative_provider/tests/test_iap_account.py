# Copyright 2022 Moka Tourisme (https://www.mokatourisme.fr).
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest import mock

from odoo.tests import TransactionCase


class IapAccountCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        res = super().setUpClass()

        cls.lead_service = cls.env.ref("iap.iap_service_reveal")
        cls.other_service = cls.env["iap.service"].create(
            {
                "name": "Other Service",
                "technical_name": "other-service",
                "description": "Other Service",
                "unit_name": "Credits",
                "integer_balance": True,
            }
        )

        return res

    def test_create_odoo_iap(self):
        account = self.env["iap.account"].create(
            {
                "name": "Odoo IAP",
                "provider": "odoo",
                "service_id": self.lead_service.id,
            }
        )
        self.assertEqual(account.service_id, self.lead_service)

    def test_create_with_mock(self):
        with mock.patch(
            "odoo.addons.iap_alternative_provider.models."
            "iap_account.IapAccount._get_service_from_provider",
            return_value=self.lead_service,
        ):
            account = self.env["iap.account"].create(
                {
                    "name": "Odoo IAP",
                    "provider": "odoo",
                    "service_id": self.other_service.id,
                }
            )
            self.assertEqual(account.service_id, self.lead_service)

    def test_write_odoo_iap(self):
        account = self.env["iap.account"].create(
            {
                "name": "Odoo IAP",
                "provider": "odoo",
                "service_id": self.lead_service.id,
            }
        )
        account.write({"service_id": self.other_service.id})
        self.assertEqual(account.service_id, self.other_service)
        account.write({"service_id": self.lead_service.id})
        with mock.patch(
            "odoo.addons.iap_alternative_provider.models."
            "iap_account.IapAccount._get_service_from_provider",
            return_value=self.lead_service,
        ):
            account.write({"service_id": self.other_service.id})
            self.assertEqual(account.service_id, self.lead_service)
