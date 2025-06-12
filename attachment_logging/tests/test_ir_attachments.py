import base64
import logging

from odoo.tests import tagged
from odoo.tools.misc import format_datetime

from odoo.addons.base.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


@tagged("-at_install", "post_install")
class TestIrAttachments(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner #1"})

    @classmethod
    def _create_attachment(cls):
        file_content = "Hi, this files is for tests."
        file_data = base64.b64encode(file_content.encode("utf-8"))
        return cls.env["ir.attachment"].create(
            {
                "name": "tst_file.txt",
                "datas": file_data,
                "res_model": cls.partner._name,
                "res_id": cls.partner.id,
                "mimetype": "text/plain",
            }
        )

    def test01_attachment_format(self):
        attachment = self._create_attachment()
        result = attachment._attachment_format()
        self.assertTrue(result)
        self.assertEqual(result[0]["create_user"], attachment.create_uid.name)
        self.assertEqual(
            result[0]["create_date"],
            format_datetime(self.env, attachment.create_date),
        )

    def test02_post_add_create(self):
        attachment = self._create_attachment()
        self.env["ir.config_parameter"].sudo().set_param(
            "attachment_logging.use_attachment_log", False
        )
        self.partner.message_ids = [
            (
                5,
                0,
            )
        ]
        attachment._post_add_create()
        self.assertEqual(len(self.partner.message_ids), 0)
        self.env["ir.config_parameter"].sudo().set_param(
            "attachment_logging.use_attachment_log", True
        )
        attachment._post_add_create()
        self.assertEqual(len(self.partner.message_ids), 1)

    def test03_delete_and_notify(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "attachment_logging.use_attachment_log", False
        )
        self.partner.message_ids = [
            (
                5,
                0,
            )
        ]
        attachment = self._create_attachment()
        attachment._delete_and_notify()
        self.assertEqual(len(self.partner.message_ids), 0)
        self.env["ir.config_parameter"].sudo().set_param(
            "attachment_logging.use_attachment_log", True
        )
        attachment = self._create_attachment()
        attachment._delete_and_notify()
        self.assertEqual(len(self.partner.message_ids), 1)
