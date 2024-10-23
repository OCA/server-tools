# Copyright 2023 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import base64

from .common import SynchronizeRecordCase

TESTFILE = "Wood Corner;updated name 1\nDeco Addict;updated name 2"


class TestImport(SynchronizeRecordCase):
    def test_import(self):
        attachment = self.env["attachment.queue"].create(
            {
                "name": "test aq",
                "fs_storage_id": self.backend.id,
                "datas": base64.b64encode(TESTFILE.encode("utf-8")),
                "file_type": "test_import",
            }
        )
        attachment.run()
        self.assertEqual(self.env.ref("base.res_partner_1").name, "updated name 1")
        self.assertEqual(self.env.ref("base.res_partner_2").name, "updated name 2")
        self.assertEqual(self.env.ref("base.res_partner_1").import_file_id, attachment)
