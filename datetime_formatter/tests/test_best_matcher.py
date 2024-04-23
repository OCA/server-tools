# Copyright 2015, 2017 Jairo Llopis <jairo.llopis@tecnativa.com>
# Copyright 2016 Tecnativa, S.L. - Vicent Cubells
# Copyright 2024 Tecnativa - Carolina Fernandez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class BasicCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(BasicCase, cls).setUpClass()
        cls.langs = (
            cls.env.ref("base.lang_en"),
            cls.env.ref("base.lang_es"),
            cls.env.ref("base.lang_it"),
            cls.env.ref("base.lang_pt"),
            cls.env.ref("base.lang_zh_CN"),
        )
        cls.rl = cls.env["res.lang"]
        for lang in cls.langs:
            cls.rl._activate_lang(lang.code)

    def test_explicit(self):
        """When an explicit lang is used."""
        for lang in self.langs:
            self.assertEqual(self.rl.best_match(lang.code).code, lang.code)

    def test_record(self):
        """When called from a ``res.lang`` record."""
        rl = self.rl.with_context(lang="it_IT")
        rl.env.user.lang = "pt_PT"
        for lang in self.langs:
            self.assertEqual(
                rl.search([("code", "=", lang.code)]).best_match().code, lang.code
            )

    def test_context(self):
        """When called with a lang in context."""
        self.env.user.lang = "pt_PT"
        for lang in self.langs:
            self.assertEqual(
                self.rl.with_context(lang=lang.code).best_match().code, lang.code
            )

    def test_user(self):
        """When lang not specified in context."""
        for lang in self.langs:
            self.env.user.lang = lang.code
            # Lang is False in context
            self.assertEqual(
                self.rl.with_context(lang=False).best_match().code, lang.code
            )
            # Lang not found in context
            self.assertEqual(self.rl.with_context(**{}).best_match().code, lang.code)

    def test_first_installed(self):
        """When falling back to first installed language."""
        first = self.rl.search([("active", "=", True)], limit=1)
        self.env.user.lang = False
        self.assertEqual(self.rl.with_context(lang=False).best_match().code, first.code)

    def test_unavailable(self):
        """When matches to an unavailable language."""
        self.env.user.lang = False
        self.rl = self.rl.with_context(lang=False)
        first = self.rl.search([("active", "=", True)], limit=1)
        # Safe mode
        self.assertEqual(self.rl.best_match("fake_LANG").code, first.code)
        # Unsafe mode
        with self.assertRaises(UserError):
            self.rl.best_match("fake_LANG", failure_safe=False)
