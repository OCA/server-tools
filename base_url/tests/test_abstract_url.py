# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from unittest import mock

from odoo_test_helper import FakeModelLoader

from odoo.tests import TransactionCase


class TestAbstractUrl(TransactionCase, FakeModelLoader):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from .models import FakeCateg, FakeProduct

        cls.loader.update_registry([FakeProduct, FakeCateg])

        cls.lang_en = cls.env.ref("base.lang_en")
        cls.lang_fr = cls.env.ref("base.lang_fr")
        cls.lang_fr.active = True
        cls.product = (
            cls.env["fake.product"]
            .with_context(lang="en_US")
            .create({"name": "My Product"})
        )
        cls.product.with_context(lang="fr_FR").name = "Mon Produit"

    def _expect_url_for_lang(self, lang, url_key):
        self.assertEqual(self.product._get_main_url("global", lang).key, url_key)

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super().tearDownClass()

    def test_update_url_key(self):
        self.product._update_url_key("global", "en_US")
        self._expect_url_for_lang("en_US", "my-product")
        url = self.product.url_ids.filtered(lambda s: s.lang_id == self.lang_en)
        self.assertEqual(len(url), 1)
        self.assertFalse(url.manual)
        self.assertFalse(url.redirect)

    def test_update_url_2_lang(self):
        self.product._update_url_key("global", "en_US")
        self.product._update_url_key("global", "fr_FR")
        self._expect_url_for_lang("en_US", "my-product")
        self._expect_url_for_lang("fr_FR", "mon-produit")
        self.assertEqual(len(self.product.url_ids), 2)

        url = self.product.url_ids.filtered(lambda s: s.lang_id == self.lang_fr)
        self.assertEqual(len(url), 1)
        self.assertFalse(url.manual)
        self.assertFalse(url.redirect)

    def test_update_no_translatable_field(self):
        self.product._update_url_key("global", "en_US")
        self.product._update_url_key("global", "fr_FR")
        self.product.write({"code": "1234"})
        self.product._update_url_key("global", "en_US")
        self.product._update_url_key("global", "fr_FR")
        self.assertEqual(len(self.product.url_ids), 4)
        redirects = self.product._get_redirect_urls("global", "en_US")
        self._expect_url_for_lang("en_US", "my-product-1234")
        self.assertEqual(len(redirects), 1)
        redirects = self.product._get_redirect_urls("global", "fr_FR")
        self.assertEqual(len(redirects), 1)
        self._expect_url_for_lang("fr_FR", "mon-produit-1234")

    def test_update_translatable_field(self):
        self.product._update_url_key("global", "en_US")
        self.product._update_url_key("global", "fr_FR")
        self.product.name = "My Product With Redirect"
        self.product._update_url_key("global", "en_US")
        self.product._update_url_key("global", "fr_FR")
        self.assertEqual(len(self.product.url_ids), 3)
        redirects = self.product._get_redirect_urls("global", "en_US")
        self._expect_url_for_lang("en_US", "my-product-with-redirect")
        self.assertEqual(len(redirects), 1)

    def test_update_product_never_generated(self):
        self.product.name = "My product never had url generated"
        self.product._update_url_key("global", "en_US")
        self._expect_url_for_lang("en_US", "my-product-never-had-url-generated")
        self.assertEqual(len(self.product.url_ids), 1)

    def test_update_with_relation(self):
        self.product._update_url_key("global", "en_US")
        categ = self.env["fake.categ"].create({"name": "Foo"})
        self.product.write({"categ_id": categ.id})
        self.product._update_url_key("global", "en_US")
        self.assertEqual(len(self.product.url_ids), 2)
        redirects = self.product._get_redirect_urls("global", "en_US")
        self.assertEqual(len(redirects), 1)
        self._expect_url_for_lang("en_US", "foo-my-product")

    def test_create_manual_url(self):
        self.env["url.url"].create(
            {
                "manual": True,
                "key": "my-custom-key",
                "lang_id": self.lang_en.id,
                "res_id": self.product.id,
                "res_model": "fake.product",
                "referential": "global",
            }
        )
        self._expect_url_for_lang("en_US", "my-custom-key")
        self.assertEqual(len(self.product.url_ids), 1)

        self.product.name = "My name have change but my url is the same"
        self.product._update_url_key("global", "en_US")
        self._expect_url_for_lang("en_US", "my-custom-key")

    def test_write_inactive(self):
        # when we deactivate a record, the redirect method should be called
        with mock.patch.object(
            self.product.__class__, "_redirect_existing_url"
        ) as mocked_redirect:
            self.product.active = False
            mocked_redirect.assert_called_once()

    def test_update_twice_write_once(self):
        """"
        When we update twice the same record, the write method should be called
        only once. This is important because for example, by default, in
        shopinvader_search_engine_update, when the method write is called,
        it mark the record as to_recompute. The recompute will then call the
        serializer method on each binding one by one and set the state to done.
        Unfortunately, if a record has 2 bindings, the serializer will call 2
        times the _update_url_key method. The first time, if every time the
        method make a write on the record, the record will end up with the
        state to_recompute.
        """ ""

        # we mock the write method to check the number of call but we want the
        # method to be executed
        original_write = self.product.write
        with mock.patch.object(type(self.product), "write") as mocked_write:
            mocked_write.side_effect = original_write
            self.product._update_url_key("global", "en_US")
            self.product._update_url_key("global", "en_US")
            mocked_write.assert_called_once()
