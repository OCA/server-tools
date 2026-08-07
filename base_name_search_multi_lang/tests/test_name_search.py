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

    def _skip_if_search_extended(self):
        # base_search_multi_lang extends every search, on purpose
        module = self.env["ir.module.module"]._get("base_search_multi_lang")
        if module.state == "installed":
            self.skipTest("base_search_multi_lang is installed")

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

    def test_name_search_multi_lang_user_lang_name(self):
        """Records found in other language are named in the user language"""
        self._enable_multi_lang()
        res = self.model.name_search("การพึ่งพาของโมดูล")
        self.assertIn((self.dependency.id, self.dependency.display_name), res)

    def test_name_search_negative_operator(self):
        """Negative operators keep the standard behavior"""
        self._skip_if_search_extended()
        self._enable_multi_lang()
        res = self.model.name_search("การพึ่งพาของโมดูล", operator="not ilike", limit=None)
        self.assertIn(self.dependency.id, [rec_id for rec_id, _name in res])

    def test_search_not_extended(self):
        """Only name_search is extended, not other searches"""
        self._skip_if_search_extended()
        self._enable_multi_lang()
        domain = [("name", "ilike", "การพึ่งพาของโมดูล")]
        self.assertFalse(self.model.search(domain))
        domain = [("display_name", "ilike", "การพึ่งพาของโมดูล")]
        self.assertFalse(self.model.search(domain))
