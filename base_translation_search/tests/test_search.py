# Copyright 2026 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo.tests import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("-at_install", "post_install")
class TranslationSearchCase(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["res.lang"]._activate_lang("th_TH")
        cls.env.ref("base.module_base")._update_translations()
        cls.model = cls.env["ir.model"]
        cls.dependency = cls.env.ref("base.model_ir_module_module_dependency")

    def _enable_translation_search(self):
        self.env.ref("base.model_ir_model").translation_search = True

    def test_search_translated_field_multi_lang(self):
        """Searching the translated field itself, as a search view does"""
        domain = [("name", "ilike", "การพึ่งพาของโมดูล")]
        self.assertFalse(self.model.search(domain))
        self._enable_translation_search()
        self.assertEqual(self.model.search(domain), self.dependency)

    def test_search_negative_operator_multi_lang(self):
        """A record matching in any language is excluded"""
        domain = [("name", "not ilike", "การพึ่งพาของโมดูล")]
        self.assertIn(self.dependency, self.model.search(domain))
        self._enable_translation_search()
        self.assertNotIn(self.dependency, self.model.search(domain))

    def test_search_equal_operator_not_extended(self):
        """Operators comparing the whole value keep the standard behavior"""
        self._enable_translation_search()
        domain = [("name", "=", "การพึ่งพาของโมดูล")]
        self.assertFalse(self.model.search(domain))

    def test_name_search_translation_search(self):
        """Many2one fields find the records in other languages too"""
        self.assertFalse(self.model.name_search("การพึ่งพาของโมดูล"))
        self._enable_translation_search()
        res = self.model.name_search("การพึ่งพาของโมดูล")
        self.assertIn((self.dependency.id, self.dependency.display_name), res)

    def test_other_model_not_extended(self):
        """Models without Translation Search keep the standard behavior"""
        self._enable_translation_search()
        group = self.env.ref("base.group_user")
        name_th = group.with_context(lang="th_TH").name
        self.assertNotEqual(name_th, group.name)
        domain = [("name", "ilike", name_th)]
        self.assertFalse(self.env["res.groups"].search(domain))
