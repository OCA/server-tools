# Copyright 2016-2017 Jairo Llopis <jairo.llopis@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tools import mute_logger
from odoo.tests.common import TransactionCase


class ExtractorCase(TransactionCase):
    def setUp(self):
        super(ExtractorCase, self).setUp()
        # Shortcut
        self.imgs_from_html = self.env["ir.fields.converter"].imgs_from_html

    def test_mixed_images_found(self):
        """Images correctly found in <img> elements and backgrounds."""
        content = u"""
            <div>
                <!-- src-less img -->
                <img/>
                <p/>
                <img src="/path/0"/>
                <img src="/path/1"/>
                <img src="/path/2"/>
                <img src="/path/3"/>
                <section style="background : URL('/path/4');;background;ö;">
                    <div style='BACKGROUND-IMAGE:url(/path/5)'>
                        <p style="background:uRl(&quot;/path/6&quot;)">
                            <img src="/path/7"/>
                        </p>
                    </div>
                </section>
            </div>
            """

        # Read all images
        for n, url in enumerate(self.imgs_from_html(content)):
            self.assertEqual("/path/%d" % n, url)
        self.assertEqual(n, 7)

        # Read only first image
        for n, url in enumerate(self.imgs_from_html(content, 1)):
            self.assertEqual("/path/%d" % n, url)
        self.assertEqual(n, 0)

    @mute_logger("odoo.addons.html_image_url_extractor" +
                 ".models.ir_fields_converter")
    def test_empty_html(self):
        """Empty HTML handled correctly."""
        for laps, text in self.imgs_from_html(""):
            self.assertTrue(False)  # You should never get here
        with self.assertRaises(Exception):
            list(self.imgs_from_html("", fail=True))

    @mute_logger("odoo.addons.html_image_url_extractor" +
                 ".models.ir_fields_converter")
    def test_false_html(self):
        """``False`` HTML handled correctly."""
        for laps, text in self.imgs_from_html(False):
            self.assertTrue(False)  # You should never get here
        with self.assertRaises(Exception):
            list(self.imgs_from_html(False, fail=True))
