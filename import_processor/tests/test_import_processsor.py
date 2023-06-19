from odoo.tests.common import TransactionCase, tagged
from odoo.modules.module import get_module_resource
from odoo.exceptions import UserError
from odoo.tools import file_open


def create_new_records():
    """Processor data handled by the safe_eval and the following variables are additionally defined"""
    return """if entry:
        rec = model.create({k: v for k, v in entry.items() if k in ["name","email","phone","street","street2", "zip", "city"]})
        records |= rec"""


@tagged("post_install", "-at_install")
class ImportProcessorTest(TransactionCase):
    @classmethod
    def setUpClass(self):
        super().setUpClass()
        # Create Import Processor record of the 'res.partner' Object
        self.import_processor = self.env["import.processor"].create(
            {
                "name": "Import Res Partner",
                "model_id": self.env["ir.model"]
                .search([("model", "=", "res.partner")])
                .id,
                "active": True,
                "file_type": "csv",
                "processor": create_new_records(),
            }
        )

    def get_file_binary_data(self, file_name):
        file_path = get_module_resource("import_processor", "tests", file_name)
        with file_open(file_path, "rb") as file:
            file_contents = file.read()
        return file_contents

    def test_check_import_processor_is_active(self):
        """Test whether a Import Processor record is active or not"""
        self.assertTrue(self.import_processor.active)

    def test_import_csv(self):
        """Test the import of data from a CSV file.

        It ensures that the import process successfully reads the CSV file,
        parses the data, and creates the corresponding records.
        """
        file = self.get_file_binary_data("res_partner_1.csv")
        record = self.import_processor.process(file)
        # Verifies the imported record
        self.assertTrue(len(record) == 1)

    def test_import_zip_one(self):
        """Test the import of data from 'zip_one.zip', which contains
        a single CSV file with one res.partner record"""

        # Compression method "Zipped File"
        self.import_processor.compression = "zip_one"
        file = self.get_file_binary_data("zip_one.zip")
        record = self.import_processor.process(file)

        # Verifies the imported record
        self.assertTrue(len(record) == 1)

    def test_import_zip_all(self):
        """Test the import of data from 'zip_all.zip', which contains
        two CSV files, each of which has one 'res.partner' record."""

        # Compression method "Multiple Zipped Files"
        self.import_processor.compression = "zip_all"
        file = self.get_file_binary_data("zip_all.zip")
        record = self.import_processor.process(file)

        # Verifies the imported record
        self.assertTrue(len(record) == 2)

    def test_import_multi_compression_zip_one(self):
        '''This case verifies the behavior of the zip_one compression method 
        when multiple files are compressed into a single ZIP file. The expected 
        outcome is that the compression process raises a Usererror exception.'''

        # Compression method "Zipped File"
        self.import_processor.compression = "zip_one"
        file = self.get_file_binary_data("zip_all.zip")
        with self.assertRaisesRegex(UserError, "Expected only 1 file."):
            self.import_processor.process(file)
