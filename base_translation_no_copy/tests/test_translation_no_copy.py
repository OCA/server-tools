# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_test_helper import FakeModelLoader

from odoo import fields, models
from odoo.tests.common import TransactionCase


class TestTranslationNoCopy(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()

        class TestModelTranslationNoCopy(models.Model):
            _name = "test.model.translation.no.copy"

            name = fields.Char(translate=True)
            descr = fields.Char(translate=True)

            def _get_field_names_to_skip_in_copy(self):
                res = super()._get_field_names_to_skip_in_copy()
                return res + ["name"]

        cls.loader.update_registry((TestModelTranslationNoCopy,))
        cls.env.ref("base.lang_en").action_unarchive()
        cls.env.ref("base.lang_it").action_unarchive()

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super().tearDownClass()

    def test_translation_no_copy(self):
        """Tests that translations are not copied

        In this test, the model does not allow copies of translations for field "name",
        therefore when we copy a record, we expect the new record to have the
        language-naive value in field "name", while other fields will still keep the
        original translation

        rec1:
             name      | descr            | lang
            -----------|------------------|-------
             Test Name | Test Description | en_US
             Nome Test | Descrizione Test | it_IT

        rec2 (copied from rec1):
             name      | descr            | lang
            -----------|------------------|-------
             Test Name | Test Description | en_US
             Test Name | Descrizione Test | it_IT

        """
        name_en = "Test Name"
        desc_en = "Test Description"
        name_it = "Nome Test"
        desc_it = "Descrizione Test"
        rec1 = self.env["test.model.translation.no.copy"].create({})
        rec1.with_context(lang="en_US").write({"name": name_en, "descr": desc_en})
        rec1.with_context(lang="it_IT").write({"name": name_it, "descr": desc_it})
        rec2 = rec1.copy()
        rec2_en = rec2.with_context(lang="en_US")
        self.assertEqual(rec2_en.name, name_en)
        self.assertEqual(rec2_en.descr, desc_en)
        rec2_it = rec2.with_context(lang="it_IT")
        self.assertEqual(rec2_it.name, name_en)  # Not translated
        self.assertEqual(rec2_it.descr, desc_it)  # Translated
