# Copyright 2015, 2017 Jairo Llopis <jairo.llopis@tecnativa.com>
# Copyright 2016 Tecnativa, S.L. - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class BasicCase(TransactionCase):
    def setUp(self):
        super().setUp()
        self.langs = ("en_US", "es_ES", "it_IT", "pt_PT", "zh_CN")
        self.rl = self.env["res.lang"]
        for lang in self.langs:
            if not self.rl.search([("code", "=", lang)]):
                self.rl.load_lang(lang)

    def test_explicit(self):
        """When an explicit lang is used."""
        for lang in self.langs:
            self.assertEqual(self.rl.best_match(lang).code, lang)

    def test_record(self):
        """When called from a ``res.lang`` record."""
        rl = self.rl.with_context(lang="it_IT")
        rl.env.user.lang = "pt_PT"

        for lang in self.langs:
            self.assertEqual(
                rl.search([("code", "=", lang)]).best_match().code,
                lang)

    def test_context(self):
        """When called with a lang in context."""
        self.env.user.lang = "pt_PT"

        for lang in self.langs:
            self.assertEqual(
                self.rl.with_context(lang=lang).best_match().code,
                lang)

    def test_user(self):
        """When lang not specified in context."""
        for lang in self.langs:
            self.env.user.lang = lang

            # Lang is False in context
            self.assertEqual(
                self.rl.with_context(lang=False).best_match().code,
                lang)

            # Lang not found in context
            self.assertEqual(
                self.rl.with_context(dict()).best_match().code,
                lang)

    def test_first_installed(self):
        """When falling back to first installed language."""
        first = self.rl.search([("active", "=", True)], limit=1)
        self.env.user.lang = False
        self.assertEqual(
            self.rl.with_context(lang=False).best_match().code,
            first.code)

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
