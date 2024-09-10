# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest import mock

from odoo import tools
from odoo.tests.common import TransactionCase


class TestOcaModuleUpdates(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.version = cls.env["oca.update.version"].create({"name": "16"})
        # Unlinking items just in case...
        cls.env["oca.update.module"].search([]).unlink()
        cls.module = cls.env["oca.update.module"].create(
            {"name": "_oca_update_test_module", "version_id": cls.version.id}
        )

    def test_feed_empty(self):
        date = self.module.last_update
        self.module.feed_data()
        self.assertFalse(self.module.last_version)
        self.assertGreater(self.module.last_update, date)

    def test_cron_empty(self):
        date = self.module.last_update
        self.env["oca.update.module"].cron_update(with_commit=False)
        self.assertFalse(self.module.last_version)
        self.assertGreater(self.module.last_update, date)

    def test_feed_filled(self):
        date = self.module.last_update
        self.assertFalse(self.module.url)
        with mock.patch("feedparser.http.get") as mock_parse:
            mock_parse.return_value = tools.file_open(
                "addons/oca_module_updates/tests/rss.xml", mode="rb"
            ).read()
            self.module.feed_data()
            mock_parse.assert_called_once()
        self.assertTrue(self.module.url)
        self.assertTrue(self.module.last_version)
        self.assertGreater(self.module.last_update, date)

    def test_cron_filled(self):
        date = self.module.last_update
        with mock.patch("feedparser.http.get") as mock_parse:
            mock_parse.return_value = tools.file_open(
                "addons/oca_module_updates/tests/rss.xml", mode="rb"
            ).read()
            self.env["oca.update.module"].cron_update(with_commit=False)
            mock_parse.assert_called_once()
        self.assertTrue(self.module.last_version)
        self.assertGreater(self.module.last_update, date)

    def test_version_creation(self):
        version = self.env["oca.update.version"].create({"name": "myversion"})
        new_version = self.env["oca.update.version"].search(
            [("name", "=", "myversion")]
        )
        self.assertEqual(version, new_version)
