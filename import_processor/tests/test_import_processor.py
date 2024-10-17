from odoo.exceptions import UserError
from odoo.modules.module import get_module_resource
from odoo.tests.common import TransactionCase, tagged
from odoo.tools import file_open


@tagged("post_install", "-at_install")
class ImportProcessorTest(TransactionCase):
    def setUp(self):
        super().setUp()
        self.import_processor_csv = self.env.ref(
            "import_processor.demo_import_processor_csv"
        )
        self.import_processor_xml = self.env.ref(
            "import_processor.demo_import_processor_xml"
        )
        self.import_processor_json = self.env.ref(
            "import_processor.demo_import_processor_json"
        )

    def _get_file_binary_data(self, file_name):
        file_path = get_module_resource("import_processor", "tests", file_name)
        with file_open(file_path, "rb") as file:
            file_contents = file.read()
        return file_contents

    def test_check_import_processor_csv_is_active(self):
        """Test whether a Import Processor record is active or not"""
        self.assertTrue(self.import_processor_csv.active)

    def test_misc(self):
        """Test functions to check if there are errors raising"""
        self.import_processor_xml._get_default_code()
        self.import_processor_xml._compute_help_text()

    def test_import_xml(self):
        """Test the import of data from a XML file.

        Preprocess: Defined variable named "regex" to validate email addresses.
        Process: Create a new record with a valid email (e.g., email.valid@example.com)
                and update record if duplicate email found.
        Postprocess: Update the "Job Description" field if it is empty.
        """
        file = self._get_file_binary_data("contacts.xml")
        record = self.import_processor_xml.process(file)
        self.assertEqual(len(record), 2)

    def test_import_json(self):
        # Test the import of data from a JSON file.

        file = self._get_file_binary_data("contacts.json")
        record = self.import_processor_json.process(file)
        self.assertEqual(len(record), 2)

    def test_import_csv_chunk(self):
        """Test the import of data from a CSV file with chunk size.

        Preprocess: Use the variable "regex" to validate email addresses.
        Process: Create a new record with a valid email (e.g., email.valid@example.com)
                and update existing records with the same email.
        Postprocess: Update the "Job Description" field if it is empty.

        """

        file = self._get_file_binary_data("contacts.csv")
        record = self.import_processor_csv.process(file)
        # Verifies the imported record
        self.assertEqual(len(record), 2)

    def test_import_zip_one(self):
        """Test the import of data from 'zip_one.zip', which contains
        a single CSV file with one res.partner record"""

        # Compression method "Zipped File"
        self.import_processor_csv.compression = "zip_one"
        file = self._get_file_binary_data("zip_one.zip")
        record = self.import_processor_csv.process(file)

        # Verifies the imported record
        self.assertEqual(len(record), 1)

    def test_import_zip_all(self):
        """Test the import of data from 'zip_all.zip', which contains
        two CSV files, each of which has one 'res.partner' record."""

        # Compression method "Multiple Zipped Files"
        self.import_processor_csv.compression = "zip_all"

        file = self._get_file_binary_data("zip_all.zip")
        record = self.import_processor_csv.process(file)
        # Verifies the imported record
        self.assertEqual(len(record), 2)

    def test_import_multi_compression_zip_one(self):
        """This case verifies the behavior of the zip_one compression method
        when multiple files are compressed into a single ZIP file. The expected
        outcome is that the compression process raises a Usererror exception."""

        # Compression method "Zipped File"
        self.import_processor_csv.compression = "zip_one"
        file = self._get_file_binary_data("zip_all.zip")
        with self.assertRaisesRegex(UserError, "Expected only 1 file."):
            self.import_processor_csv.process(file)
