# Copyright 2020 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from io import BytesIO

from .common import MockServerCase


class TestMockServer(MockServerCase):
    """Test MockServer."""

    def setUp(self):
        super(TestMockServer, self).setUp()
        server_model = self.env["server.ftp"]
        server = server_model.create(
            {
                "name": "Mock FTP Server for testing",
                "server_type": "mock",
                "host": "example.acme.com",
                "user": "anonymous",
                "password": "password",
                "state": "draft",
            }
        )
        folder_model = self.env["server.ftp.folder"]
        self.folder = folder_model.create(
            {
                "name": "Mock FTP Folder",
                "server_id": server.id,
                "path": "example_directory",
            }
        )

    def test_mock_server(self):
        """Test Mock FTP Server."""
        folder = self.folder
        server = folder.server_id
        server.action_test_connection()
        self.assertEqual(server.state, "done")
        directory = folder.connect()
        self.assertEqual(directory.listdir(), [])
        datas = BytesIO()
        datas.write(b"Hello World!")
        directory.putfo(datas, "hello.txt")
        self.assertEqual(directory.listdir(), ["hello.txt"])
        self.assertTrue(directory.exists("hello.txt"))
        self.assertFalse(directory.exists("bye.txt"))
        get_datas = BytesIO()
        directory.getfo("hello.txt", get_datas)
        get_datas.seek(0)
        hello_bytes = get_datas.read()
        self.assertEqual(hello_bytes, b"Hello World!")
        directory.remove("hello.txt")
        self.assertFalse(directory.exists("hello.txt"))
        self.assertEqual(directory.listdir(), [])
        directory.close()
