# Copyright 2016-2017 Tecnativa - Jairo Llopis
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


class ExtractorCase(TransactionCase):
    def setUp(self):
        super().setUp()
        # Shortcut
        self.imgs_from_html = self.env["ir.fields.converter"].imgs_from_html

    def test_mixed_images_found(self):
        """Images correctly found in <img> elements and backgrounds."""
        content = """
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

    @mute_logger("odoo.addons.html_image_url_extractor" + ".models.ir_fields_converter")
    def test_empty_html(self):
        """Empty HTML handled correctly."""
        self.assertTrue(enumerate(self.imgs_from_html("")))
        with self.assertRaisesRegex(Exception, "Document is empty"):
            list(self.imgs_from_html("", fail=True))

    @mute_logger("odoo.addons.html_image_url_extractor" + ".models.ir_fields_converter")
    def test_false_html(self):
        """``False`` HTML handled correctly."""
        self.assertTrue(enumerate(self.imgs_from_html(False)))
        with self.assertRaisesRegex(Exception, "expected string or bytes-like object"):
            list(self.imgs_from_html(False, fail=True))
