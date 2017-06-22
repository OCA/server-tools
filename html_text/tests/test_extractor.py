# -*- coding: utf-8 -*-
# Copyright 2016-2017 Jairo Llopis <jairo.llopis@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from lxml import etree
from odoo.tools import mute_logger
from odoo.tests.common import TransactionCase
from ..models import ir_fields_converter


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

    @mute_logger(ir_fields_converter.__name__)
    def test_empty_html(self):
        """Empty HTML handled correctly."""
        self.assertEqual(self.text_from_html(""), "")
        with self.assertRaises(etree.XMLSyntaxError):
            self.text_from_html("", fail=True)

    @mute_logger(ir_fields_converter.__name__)
    def test_false_html(self):
        """``False`` HTML handled correctly."""
        self.assertEqual(self.text_from_html(False), "")
        with self.assertRaises(TypeError):
            self.text_from_html(False, fail=True)

    @mute_logger(ir_fields_converter.__name__)
    def test_bad_html(self):
        """Bad HTML handled correctly."""
        self.assertEqual(self.text_from_html("<<bad>"), "")
        with self.assertRaises(etree.ParserError):
            self.text_from_html("<<bad>", fail=True)
