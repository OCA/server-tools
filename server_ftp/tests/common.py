# Copyright 2020 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
"""Define a class that can be used in Custom Modules to test FTP interactions."""
from odoo.tests.common import TransactionCase


class MockServerCase(TransactionCase):
    """Test MockServer."""

    def setUp(self):
        super().setUp()
        server_model = self.env["server.ftp"]
        self.server = server_model.create(
            {
                "name": "Mock FTP Server for testing",
                "server_type": "mock",
                "host": "example.acme.com",
                "user": "anonymous",
                "state": "draft",
            }
        )
        folder_model = self.env["server.ftp.folder"]
        self.folder = folder_model.create(
            {
                "name": "Mock FTP Folder",
                "server_id": self.server.id,
                "path": "example_directory",
            }
        )
