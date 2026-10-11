# Copyright 2020 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo.tests import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("-at_install", "post_install")
class NameSearchCase(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["res.lang"]._activate_lang("th_TH")
        cls.env.ref("base.module_base")._update_translations()
        cls.model = cls.env["ir.model"]
        cls.dependency = cls.env.ref("base.model_ir_module_module_dependency")

    def _enable_multi_lang(self):
        self.env.ref("base.model_ir_model").name_search_multi_lang = True

    def test_name_search_normal(self):
        """Search for a model name in other language, not found"""
        res = self.model.name_search("Module dependency")
        self.assertTrue(res)
        res = self.model.name_search("การพึ่งพาของโมดูล")
        self.assertFalse(res)  # Not found in other language

    def test_name_search_multi_lang(self):
        """Search for a model name in other language, found it"""
        self._enable_multi_lang()
        res = self.model.name_search("Module dependency")
        self.assertTrue(res)
        res = self.model.name_search("การพึ่งพาของโมดูล")
        self.assertTrue(res)  # Found it even in other language

    def test_search_translated_field_multi_lang(self):
        """Searching the translated field itself, as a search view does"""
        domain = [("name", "ilike", "การพึ่งพาของโมดูล")]
        self.assertFalse(self.model.search(domain))
        self._enable_multi_lang()
        self.assertEqual(self.model.search(domain), self.dependency)

    def test_search_negative_operator_multi_lang(self):
        """A record matching in any language is excluded"""
        domain = [("name", "not ilike", "การพึ่งพาของโมดูล")]
        self.assertIn(self.dependency, self.model.search(domain))
        self._enable_multi_lang()
        self.assertNotIn(self.dependency, self.model.search(domain))
