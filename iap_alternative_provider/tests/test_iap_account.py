# Copyright 2022 Moka Tourisme (https://www.mokatourisme.fr).
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest import mock

from odoo.tests import TransactionCase


class IapAccountCase(TransactionCase):
    def test_create_odoo_iap(self):
        account = self.env["iap.account"].create(
            {
                "name": "Odoo IAP",
                "provider": "odoo",
                "service_name": "some-service",
            }
        )
        self.assertEqual(account.service_name, "some-service")

    def test_create_with_mock(self):
        with mock.patch(
            "odoo.addons.iap_alternative_provider.models."
            "iap_account.IapAccount._get_service_from_provider",
            return_value="other-service",
        ):
            account = self.env["iap.account"].create(
                {
                    "name": "Odoo IAP",
                    "provider": "odoo",
                    "service_name": "some-service",
                }
            )
            self.assertEqual(account.service_name, "other-service")

    def test_write_odoo_iap(self):
        account = self.env["iap.account"].create(
            {
                "name": "Odoo IAP",
                "provider": "odoo",
                "service_name": "",
            }
        )
        self.assertEqual(account.service_name, "")
        account.write({"service_name": "some-service"})
        self.assertEqual(account.service_name, "some-service")
        with mock.patch(
            "odoo.addons.iap_alternative_provider.models."
            "iap_account.IapAccount._get_service_from_provider",
            return_value="other-service",
        ):
            account.write({"service_name": "some-service-2"})
            self.assertEqual(account.service_name, "other-service")
