# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest import mock

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
        result = self.backend.fs.ls("test_export", detail=False)
        self.assertEqual(result, ["test_export/foo.txt"])

    @mute_logger("odoo.addons.attachment_queue.models.attachment_queue")
    def test_failing_export(self):
        with mock.patch.object(
            type(self.backend.fs),
            "open",
            side_effect=raising_side_effect,
        ):
            self.attachment.with_context(queue_job__no_delay=True).run_as_job()
        self.assertEqual(self.attachment.state, "failed")
        self.assertEqual(self.attachment.state_message, "Boom")
