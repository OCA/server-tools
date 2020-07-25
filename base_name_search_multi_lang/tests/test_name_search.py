# Copyright 2020 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo.tests.common import TransactionCase, at_install, post_install


@at_install(False)
@post_install(True)
class NameSearchCase(TransactionCase):
    def setUp(self):
        super(NameSearchCase, self).setUp()
        # Install another language, th_TH
        self.env["res.lang"].load_lang("th_TH")
        self.env.ref("base.module_base")._update_translations()

    def test_name_search_normal(self):
        """ Search for a model name in other language, not found """
        res = self.env["ir.model"].name_search("Module dependency")
        self.assertTrue(res)
        res = self.env["ir.model"].name_search("การพึ่งพาของโมดูล")
        self.assertFalse(res)  # Not found in other language

    def test_name_search_multi_lang(self):
        """ Search for a model name in other language, found it """
        self.env.ref("base.model_ir_model").name_search_multi_lang = True
        res = self.env["ir.model"].name_search("Module dependency")
        self.assertTrue(res)
        res = self.env["ir.model"].name_search("การพึ่งพาของโมดูล")
        self.assertTrue(res)  # Found it even in other language
