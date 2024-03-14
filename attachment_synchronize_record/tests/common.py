# Copyright 2023 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import uuid

from odoo_test_helper import FakeModelLoader

from odoo.addons.attachment_synchronize.tests.common import SyncCommon


class SynchronizeRecordCommon(SyncCommon):
    # pylint: disable=W8106
    def setUp(self):
        super().setUp()
        # SyncCommon setUp() overwrites this so we set it again
        self.backend = self.env.ref(
            "attachment_synchronize.export_to_filestore"
        ).backend_id

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.backend = cls.env["fs.storage"].create(
            {
                "name": "test storage",
                "code": "test_storage",
            }
        )
        cls.backend.directory_path = str(uuid.uuid1()) + "/"
        cls.aq_before = cls.env["attachment.queue"].search([])

    def assertNewAttachmentQueue(self, n=1, domain=False):
        if not domain:
            domain = []
        aq_after = self.env["attachment.queue"].search(domain)
        self.assertEqual(len(aq_after - self.aq_before), n)
        return aq_after


class SynchronizeRecordCase(SynchronizeRecordCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.ref(
            "attachment_synchronize.export_to_filestore"
        ).backend_id = cls.backend
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from .model import AttachmentQueue, ResPartner

        cls.loader.update_registry((ResPartner, AttachmentQueue))

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super().tearDownClass()
