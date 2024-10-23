# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase


class TestUrl(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_url(self):
        video = self.env.ref("base_video_link.video_video_1")
        self.assertEqual(video.url, "https://www.youtube.com/watch?v=6JByIDOnuv8")
        self.assertEqual(
            video.thumbnail_url, "https://img.youtube.com/vi/6JByIDOnuv8/0.jpg"
        )
