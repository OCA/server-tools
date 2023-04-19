# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest import mock

from odoo_test_helper import FakeModelLoader

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase

from odoo.addons.queue_job.exception import RetryableJobError
from odoo.addons.queue_job.tests.common import trap_jobs

DUMMY_AQ_VALS = {
    "datas": "",
    "name": "dummy_aq.doc",
}
MOCK_PATH_RUN = (
    "odoo.addons.attachment_queue.models.attachment_queue.AttachmentQueue._run"
)


class TestAttachmentBaseQueue(TransactionCase):
    def _create_dummy_attachment(self, override=False, no_job=False):
        override = override or {}
        vals = DUMMY_AQ_VALS.copy()
        vals.update(override)
        if no_job:
            return (
                self.env["attachment.queue"].with_context(test_queue_job_no_delay=True)
            ).create(vals)
        return self.env["attachment.queue"].create(vals)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from .test_models import AttachmentQueue

        cls.loader.update_registry((AttachmentQueue,))

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.loader.restore_registry()
        return super().tearDownClass()

    def setUp(self):
        super().setUp()
        self.aq_model = self.env["attachment.queue"]

    def test_job_created(self):
        with trap_jobs() as trap:
            self._create_dummy_attachment()
            trap.assert_enqueued_job(
                self.env["attachment.queue"].run,
            )

    def test_aq_locked_job(self):
        """If an attachment is already running, and a job tries to run it, retry later"""
        with self.assertRaises(RetryableJobError):
            self._create_dummy_attachment({"running_lock": True}, no_job=True)

    def test_aq_locked_button(self):
        """If an attachment is already running, and a user tries to run it manually,
        raise error window"""
        attachment = self._create_dummy_attachment(no_job=True)
        attachment.running_lock = True
        with self.assertRaises(UserError):
            attachment.button_manual_run()

    def test_run_ok(self):
        """Attachment queue should have correct state and result"""
        partners_initial = len(self.env["res.partner"].search([]))
        with mock.patch.object(
            type(self.aq_model),
            "_run",
            self.env["attachment.queue"].mock_run_create_partners,
        ):
            attachment = self._create_dummy_attachment(no_job=True)
            partners_after = len(self.env["res.partner"].search([]))
            self.assertEqual(partners_after, partners_initial + 10)
            self.assertEqual(attachment.state, "done")

    def test_run_fails(self):
        """Attachment queue should have correct state/error message"""
        with mock.patch.object(
            type(self.aq_model), "_run", self.env["attachment.queue"].mock_run_fail
        ):
            attachment = self._create_dummy_attachment(no_job=True)
            self.assertEqual(attachment.state, "failed")
            self.assertEqual(attachment.state_message, "boom")

    def test_run_fails_rollback(self):
        """In case of failure, no side effects should occur"""
        partners_initial = len(self.env["res.partner"].search([]))
        with mock.patch.object(
            type(self.aq_model),
            "_run",
            self.env["attachment.queue"].mock_run_create_partners_and_fail,
        ):
            self._create_dummy_attachment(no_job=True)
            partners_after = len(self.env["res.partner"].search([]))
            self.assertEqual(partners_after, partners_initial)

    def test_set_done(self):
        """Test set_done manually"""
        attachment = self._create_dummy_attachment()
        self.assertEqual(attachment.state, "pending")
        attachment.set_done()
        self.assertEqual(attachment.state, "done")
