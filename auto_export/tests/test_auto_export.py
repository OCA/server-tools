# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import contextlib
import csv
import logging
import os
from os.path import join as opj

from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase

DATA_DIR = opj(os.path.dirname(__file__), "generated_exports")
_logger = logging.getLogger(__name__)


def _escape(s):
    """
    Taken from https://github.com/acsone/acsoo/blob/master/acsoo/tools.py
    """
    s = s.replace("\\", "\\\\")
    s = s.replace('"', '\\"')
    s = s.replace("'", "\\'")
    s = s.replace("&", "\\&")
    s = s.replace("|", "\\|")
    s = s.replace(">", "\\>")
    s = s.replace("<", "\\<")
    s = s.replace(" ", "\\ ")
    return s


@contextlib.contextmanager
def working_directory(path):
    """
    A context manager which changes the working directory to the given
    path, and then changes it back to its previous value on exit.
    Taken from https://github.com/acsone/acsoo/blob/master/acsoo/tools.py
    """
    prev_cwd = os.getcwd()
    _logger.debug(".$ cd %s", _escape(path))
    os.chdir(path)
    try:
        yield
    finally:
        # empty directory
        for file_name in os.listdir(path):
            file_path = os.path.join(path, file_name)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            # pylint:disable=broad-except
            except Exception:
                _logger.exception("Error while removing exported files")
        _logger.debug(".$ cd %s", _escape(prev_cwd))
        os.chdir(prev_cwd)


class TestAutoExport(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # MODELS
        cls.auto_export_model = cls.env["auto.export"]
        cls.ir_exports_model = cls.env["ir.exports"]
        cls.ir_model_model = cls.env["ir.model"]
        cls.ir_model_partner = cls.ir_model_model.search(
            [("model", "=", "res.partner")], limit=1
        )
        cls.queue_job_model = cls.env["queue.job"]
        # INSTANCES
        # Odoo Exports
        cls.ir_exports_partner_01 = cls.ir_exports_model.create(
            {
                "name": "Test Ir Exports Partner 01",
                "resource": cls.ir_model_partner.model,
                "export_fields": [
                    (0, 0, {"name": "id"}),
                    (0, 0, {"name": "street"}),
                    (0, 0, {"name": "email"}),
                ],
            }
        )
        # Auto Export Templates
        os.makedirs(DATA_DIR, exist_ok=True)
        cls.auto_export_01 = cls.auto_export_model.create(
            {
                "name": "Test Auto Export 01",
                "ir_model_id": cls.ir_model_partner.id,
                "ir_export_id": cls.ir_exports_partner_01.id,
                "technical_domain": "[('is_company', '=',  False)]",
                "filename_prefix": "test_partners_export",
                "filesystem_path": DATA_DIR,
            }
        )

    def _check_header(self, header, ir_exports):
        self.assertEqual(len(header), len(ir_exports.export_fields))
        for i, field_name in enumerate(header):
            self.assertEqual(field_name, ir_exports.export_fields[i].name)

    def _check_values(self, csv_read, ir_exports):
        header = []
        for row in csv_read:
            if not header:
                header = row
                self._check_header(header, ir_exports)
                continue
            if header[0] != "id":
                break
            obj = False
            for i, value in enumerate(row):
                if not obj:
                    obj = self.env.ref(value)
                    continue
                if not value:
                    value = False
                self.assertEqual(obj[header[i]], value)

    def test_auto_export_01(self):
        """
        Data:
            - An existing Auto Export template
            - File path exists
        Test case:
            - Exports data
        Expected result:
            - The export file is generated and content is consistent
        """
        with working_directory(DATA_DIR):
            full_filename = self.auto_export_01._export_data()
            self.assertTrue(os.path.exists(full_filename))
            with open(full_filename, "r") as csv_file:
                csv_read = csv.reader(csv_file, delimiter=",", quotechar='"')
                # check preview count
                self.assertEqual(
                    self.auto_export_01.preview_recordset_count,
                    len(list(csv_read)) - 1,
                )
                # check exported values
                self._check_values(csv_read, self.auto_export_01.ir_export_id)

    def test_auto_export_02(self):
        """
        Data:
            - An existing Auto Export template
            - File path does not exist
        Test case:
            - Exports data
        Expected result:
            - UserError is raised because the path doesn't exist
        """
        self.auto_export_01.filesystem_path = "not_valid_path"
        with working_directory(DATA_DIR), self.assertRaises(UserError):
            self.auto_export_01._export_data()

    def test_auto_export_03(self):
        """
        Data:
            - An existing Auto Export template
            - File path exists
        Test case:
            - Empty the file path
        Expected result:
            - ValidationError is raised
        """
        with self.assertRaises(ValidationError):
            self.auto_export_01.filesystem_path = False

    def test_auto_export_04(self):
        """
        Data:
            - An existing Auto Export template
            - File path exists
        Test case:
            - Set a model that doesn't math the ir.export
        Expected result:
            - ValidationError is raised
        """
        with self.assertRaises(ValidationError):
            self.auto_export_01.ir_model_id = self.ir_model_model.search(
                [("model", "=", "res.users")], limit=1
            )

    def test_auto_export_05(self):
        """
        Data:
            - An existing Auto Export template
            - File path exists
        Test case:
            - Set a transient model
        Expected result:
            - ValidationError is raised
        """
        with self.assertRaises(ValidationError):
            self.auto_export_01.ir_model_id = self.ir_model_model.search(
                [("transient", "=", True)], limit=1
            )

    def test_auto_export_06(self):
        """
        Data:
            - An existing Auto Export template
            - File path exists
        Test case:
            - Trigger asynchronous export
        Expected result:
            - The export job is created
        """
        self.assertFalse(
            self.queue_job_model.search([("model_name", "=", "auto.export")])
        )
        with working_directory(DATA_DIR):
            self.auto_export_01.trigger_export()
            self.assertTrue(
                self.queue_job_model.search([("model_name", "=", "auto.export")])
            )
