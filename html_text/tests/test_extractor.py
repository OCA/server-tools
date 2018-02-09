# -*- coding: utf-8 -*-
# © 2016 Grupo ESOC Ingeniería de Servicios, S.L.U. - Jairo Llopis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase
from openerp.tools import mute_logger


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

    @mute_logger("openerp.addons.html_text.models.ir_fields_converter")
    def test_empty_html(self):
        """Empty HTML handled correctly."""
        self.assertEqual(self.text_from_html(""), "")
        with self.assertRaises(Exception):
            self.text_from_html("", fail=True)

    @mute_logger("openerp.addons.html_text.models.ir_fields_converter")
    def test_false_html(self):
        """``False`` HTML handled correctly."""
        self.assertEqual(self.text_from_html(False), "")
        with self.assertRaises(Exception):
            self.text_from_html(False, fail=True)
