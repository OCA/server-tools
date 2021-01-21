# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import mock
from odoo_test_helper import FakeModelLoader

from odoo.exceptions import ValidationError
from odoo.tests import SavepointCase


class TestAbstractUrl(SavepointCase, FakeModelLoader):
    @classmethod
    def setUpClass(cls):
        super(TestAbstractUrl, cls).setUpClass()
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from .models import ResPartner, ResPartnerAddressableFake, UrlBackendFake

        cls.loader.update_registry(
            (UrlBackendFake, ResPartner, ResPartnerAddressableFake)
        )

        cls.lang = cls.env.ref("base.lang_en")
        cls.UrlUrl = cls.env["url.url"]
        cls.ResPartnerAddressable = cls.env["res.partner.addressable.fake"]
        cls.url_backend = cls.env["url.backend.fake"].create({"name": "fake backend"})
        cls.name = "partner name"
        cls.auto_key = "partner-name"

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super(TestAbstractUrl, cls).tearDownClass()

    def _get_default_partner_value(self):
        return {
            "name": self.name,
            "lang_id": self.lang.id,
            "url_builder": "auto",
            "backend_id": self.url_backend.id,
        }

    def _create_auto(self):
        return self.ResPartnerAddressable.create(self._get_default_partner_value())

    def _check_url_key(self, partner_addressable, key_name):
        self.assertFalse(partner_addressable.is_urls_sync_required)
        self.assertEqual(partner_addressable.url_key, key_name)
        self.assertEqual(len(partner_addressable.url_url_ids), 1)
        url_url = partner_addressable.url_url_ids
        self.assertEqual(url_url.url_key, key_name)
        self.assertEqual(url_url.lang_id, self.lang)
        self.assertEqual(url_url.model_id, partner_addressable)

    def test_create_auto_url(self):
        my_partner = self.ResPartnerAddressable.create(
            self._get_default_partner_value()
        )
        self._check_url_key(my_partner, self.auto_key)

    def test_create_manual_url_contrains(self):
        value = self._get_default_partner_value()
        value["url_builder"] = "manual"
        with self.assertRaises(ValidationError):
            self.ResPartnerAddressable.create(value)
        value["manual_url_key"] = "my url key"
        res = self.ResPartnerAddressable.create(value)
        self.assertTrue(res)

    def test_create_manual_url(self):
        value = self._get_default_partner_value()
        manual_url_key = "manual-url key"
        value.update({"url_builder": "manual", "manual_url_key": manual_url_key})
        my_partner = self.ResPartnerAddressable.create(value)
        self.assertTrue(my_partner)
        self._check_url_key(my_partner, manual_url_key)

    def test_write_url_builder_constrains(self):
        my_partner = self._create_auto()
        with self.assertRaises(ValidationError):
            my_partner.url_builder = "manual"
        my_partner.write({"url_builder": "manual", "manual_url_key": "manual url key"})

    def test_write_url_builder(self):
        # tests that a new url is created we update the url builder
        my_partner = self._create_auto()
        self._check_url_key(my_partner, "partner-name")
        manual_url_key = "manual-url key"
        my_partner.write({"url_builder": "manual", "manual_url_key": manual_url_key})
        my_partner.refresh()
        url_keys = set(my_partner.mapped("url_url_ids.url_key"))
        self.assertSetEqual(url_keys, {manual_url_key, self.auto_key})
        # if we reset the auto key, no new url.url should be created
        my_partner.write({"url_builder": "auto"})
        my_partner.refresh()
        self.assertEqual(2, len(my_partner.url_url_ids))
        url_keys = set(my_partner.mapped("url_url_ids.url_key"))
        self.assertSetEqual(url_keys, {manual_url_key, self.auto_key})

    def test_write_launching_automatic_url_key(self):
        my_partner = self._create_auto()
        my_partner.name = "my new name"
        my_partner.refresh()
        self.assertEqual(2, len(my_partner.url_url_ids))
        url_keys = set(my_partner.mapped("url_url_ids.url_key"))
        self.assertSetEqual(url_keys, {"my-new-name", self.auto_key})

    def test_write_inactive(self):
        my_partner = self._create_auto()
        # when we deactivate a record, the redirect method should be called
        with mock.patch.object(
            self.ResPartnerAddressable.__class__, "_redirect_existing_url"
        ) as mocked_redirect:
            my_partner.active = False
            mocked_redirect.assert_called_once()
