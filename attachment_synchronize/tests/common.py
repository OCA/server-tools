# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os

from odoo.addons.storage_backend.tests.common import CommonCase


class SyncCommon(CommonCase):
    def _clean_testing_directory(self):
        for test_dir in [
            self.directory_input,
            self.directory_output,
            self.directory_archived,
        ]:
            for filename in self.backend.list_files(test_dir):
                self.backend.delete(os.path.join(test_dir, filename))

    def _create_test_file(self):
        self.backend.add(
            os.path.join(self.directory_input, "bar.txt"),
            self.filedata,
            mimetype="text/plain",
            binary=False,
        )

    def setUp(self):
        super().setUp()
        self.directory_input = "test_import"
        self.directory_output = "test_export"
        self.directory_archived = "test_archived"
        self._clean_testing_directory()
        self._create_test_file()
        self.task = self.env.ref("attachment_synchronize.import_from_filestore")

    def tearDown(self):
        self._clean_testing_directory()
        super().tearDown()
