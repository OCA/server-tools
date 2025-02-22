# Copyright 2016-2017 Jairo Llopis <jairo.llopis@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


class ExtractorCase(TransactionCase):
    def setUp(self):
        super().setUp()
        # Shortcut
        self.text_from_html = self.env["ir.fields.converter"].text_from_html

    def test_excerpts(self):
        """Text gets correctly extracted."""
        html = """
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
            "I'm a title I'm a paragraph ¡Pues yo soy español!",
        )
        self.assertEqual(
            self.text_from_html(html, 8), "I'm a title I'm a paragraph ¡Pues yo…"
        )
        self.assertEqual(
            self.text_from_html(html, 8, 31), "I'm a title I'm a paragraph ¡P…"
        )
        self.assertEqual(
            self.text_from_html(html, 7, ellipsis=""),
            "I'm a title I'm a paragraph ¡Pues",
        )

    @mute_logger("odoo.addons.html_text.models.ir_fields_converter")
    def test_empty_html(self):
        """Empty HTML handled correctly."""
        self.assertEqual(self.text_from_html(""), "")
        with self.assertRaises(etree.ParserError):
            self.text_from_html("", fail=True)

    @mute_logger("odoo.addons.html_text.models.ir_fields_converter")
    def test_false_html(self):
        """``False`` HTML handled correctly."""
        self.assertEqual(self.text_from_html(False), "")
        with self.assertRaises(TypeError):
            self.text_from_html(False, fail=True)
