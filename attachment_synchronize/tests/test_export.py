# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import mock

from odoo.tools import mute_logger

from .common import SyncCommon


def raising_side_effect(*args, **kwargs):
    raise Exception("Boom")


class TestExport(SyncCommon):
    def setUp(self):
        super().setUp()
        self.task = self.env.ref("attachment_synchronize.export_to_filestore")
        self.attachment = self.env["attachment.queue"].create(
            {
                "name": "foo.txt",
                "task_id": self.task.id,
                "file_type": "export",
                "datas": self.filedata,
            }
        )

    def test_export(self):
        self.attachment.run()
        result = self.backend._list("test_export")
        self.assertEqual(result, ["foo.txt"])

    @mute_logger("odoo.addons.attachment_queue.models.attachment_queue")
    def test_failing_export(self):
        with mock.patch.object(
            type(self.backend),
            "_add_b64_data",
            side_effect=raising_side_effect,
        ):
            self.attachment.run()
        self.assertEqual(self.attachment.state, "failed")
        self.assertEqual(self.attachment.state_message, "Boom")
