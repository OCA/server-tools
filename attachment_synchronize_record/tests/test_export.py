# Copyright 2023 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import base64

from .common import SynchronizeRecordCase

EXPECTED_RESULT = b"Wood Corner\r\nDeco Addict\r\n"


class TestExport(SynchronizeRecordCase):
    def test_export_records(self):
        partners = self.env.ref("base.res_partner_1") + self.env.ref(
            "base.res_partner_2"
        )
        new_aq = partners.synchronize_export()
        self.assertEqual(base64.b64decode(new_aq.datas), EXPECTED_RESULT)
