# -*- coding: utf-8 -*-
# © 2016 Grupo ESOC Ingeniería de Servicios, S.L.U. - Jairo Llopis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from lxml import etree
from openerp.tests.common import TransactionCase


class ExtractorCase(TransactionCase):
    def setUp(self):
        super(ExtractorCase, self).setUp()

        # Shortcut
        self.text_from_html = self.env["ir.fields.converter"].text_from_html

    def test_excerpts(self):
        """Text gets correctly extracted."""
        html = u"""
            <html>
                <body>
                    <div class="this should not appear">
                        <h1>I'm a title</h1>
                        <p>I'm a paragraph</p>
                        <small>¡Pues yo soy español!</small>
                    </div>
                </body>
            </html>
            """

        self.assertEqual(
            self.text_from_html(html),
            u"I'm a title I'm a paragraph ¡Pues yo soy español!")
        self.assertEqual(
            self.text_from_html(html, 8),
            u"I'm a title I'm a paragraph ¡Pues yo…")
        self.assertEqual(
            self.text_from_html(html, 8, 31),
            u"I'm a title I'm a paragraph ¡P…")
        self.assertEqual(
            self.text_from_html(html, 7, ellipsis=""),
            u"I'm a title I'm a paragraph ¡Pues")

    def test_empty_html(self):
        """Empty HTML handled correctly."""
        self.assertEqual(self.text_from_html(""), "")
        with self.assertRaises(etree.XMLSyntaxError):
            self.text_from_html("", fail=True)

    def test_bad_html(self):
        """Bad HTML handled correctly."""
        self.assertEqual(self.text_from_html("<<bad>"), "")
        with self.assertRaises(etree.ParserError):
            self.text_from_html("<<bad>", fail=True)
