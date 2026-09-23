import base64
from pathlib import Path

from odoo.exceptions import UserError
from odoo.tests import Form
from odoo.tests.common import TransactionCase, tagged
from odoo.tools import file_open

from odoo.addons.import_processor.models.import_processor import chunking


@tagged("post_install", "-at_install")
class ImportProcessorTest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.import_processor_csv = cls.env["import.processor"].create(
            {
                "name": "Import Res Partner(CSV with chunk size)",
                "model_id": cls.env.ref("base.model_res_partner").id,
                "active": 1,
                "file_type": "csv",
                "chunk_size": 2,
                "preprocessor": """
regex = r"^[a-z0-9]+[\\._]?[a-z0-9]+[@][a-zA-Z]+[.][a-zA-Z]{2,3}$"
fields_list = ["name", "email", "phone", "street", "street2", "zip", "city"]
""",
                "processor": """
for contact in entry:
  email = contact.get("email")
  if re.search(regex, email):
    data = {key: value for key, value in contact.items() if key in fields_list}
    rec = model.search([("email", "=", email)])
    if rec:
      rec.update(data)
    else:
      rec = model.create(data)

    records |= rec
""",
                "postprocessor": "log('Processed the following records: %s', records)",
            }
        )
        cls.import_processor_xml = cls.env["import.processor"].create(
            {
                "name": "Import Res Partner (XML)",
                "model_id": cls.env.ref("base.model_res_partner").id,
                "active": 1,
                "file_type": "xml",
                "xml_path_entry": "//Customer",
                "preprocessor": """
# Regex Email Validation
regex = r"^[a-z0-9]+[\\._]?[a-z0-9]+[@][a-zA-Z]+[.][a-zA-Z]{2,3}$"

fields_list = ["name", "email", "phone", "street", "street2", "zip", "city"]

# Converts XML file to Dictionary
def xml_to_dict(xml_element):
  result = {}
  for child in xml_element:
    if len(child) == 0:
      result[child.tag] = child.text
    else:
      result[child.tag] = xml_to_dict(child)
  return result
""",
                "processor": """
entry = xml_to_dict(entry)

email = entry.get("email")
if re.search(regex, email):
  rec = model.search([("email", "=", email)])
  data = {key: value for key, value in entry.items() if key in fields_list}
  if rec:
    rec.update(data)
  else:
    rec = model.create(data)

  records |= rec
""",
                "postprocessor": "log('Processed the following records: %s', records)",
            }
        )
        cls.import_processor_json = cls.env["import.processor"].create(
            {
                "name": "Import Res Partner (JSON)",
                "model_id": cls.env.ref("base.model_res_partner").id,
                "active": 1,
                "file_type": "json",
                "json_path_entry": "'contact'",
                "preprocessor": """
# Regex Email Validation
regex = r"^[a-z0-9]+[\\._]?[a-z0-9]+[@][a-zA-Z]+[.][a-zA-Z]{2,3}$"
fields_list = ["name", "email", "phone", "street", "street2", "zip", "city"]
""",
                "processor": """
for contact in entry:
  email = contact.get("email")
  if re.search(regex, email):
    rec = model.search([("email", "=", email)])
    data = {key: value for key, value in contact.items() if key in fields_list}
    if rec:
      rec.update(data)
    else:
      rec = model.create(data)

    records |= rec
""",
                "postprocessor": "log('Processed the following records: %s', records)",
            }
        )

    def _get_file_binary_data(self, file_name):
        file_path = Path(__file__).parent / file_name
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

    def test_wizard_action_import_csv(self):
        file_data = self._get_file_binary_data("contacts.csv")
        encoded_data = base64.b64encode(file_data)
        count_before = self.env["res.partner"].search_count([])
        wizard = self.env["import.processor.wizard"].create(
            {
                "model": "res.partner",
                "processor_id": self.import_processor_csv.id,
                "file_upload": encoded_data,
            }
        )
        wizard.action_import()
        count_after = self.env["res.partner"].search_count([])
        self.assertEqual(
            count_before + 2, count_after, "Wizard should have created 2 partners"
        )

    def test_wizard_onchange_model(self):
        file_data = self._get_file_binary_data("contacts.csv")
        encoded_data = base64.b64encode(file_data)
        with Form(self.env["import.processor.wizard"]) as wizard_form:
            wizard_form.model = "res.partner"
            wizard_form.processor_id = self.import_processor_csv
            wizard_form.file_upload = encoded_data
            self.assertEqual(
                wizard_form.model,
                self.import_processor_csv.model_name,
                "The onchange should have set the model of the processor.",
            )

    def test_chunking_standard(cls):
        items = [1, 2, 3, 4, 5, 6]
        result = list(chunking(items, 2))
        expected = [[1, 2], [3, 4], [5, 6]]
        cls.assertEqual(result, expected)

    def test_chunking_with_remainder(cls):
        items = [1, 2, 3, 4, 5, 6, 7]
        result = list(chunking(items, 3))
        expected = [[1, 2, 3], [4, 5, 6], [7]]
        cls.assertEqual(result, expected)

    def test_chunking_size_zero_or_less(cls):
        items = [1, 2, 3]
        result = list(chunking(items, 0))
        cls.assertEqual(result, [1, 2, 3])

    def test_chunking_empty_list(cls):
        items = []
        result = list(chunking(items, 5))
        cls.assertEqual(result, [])

    def test_get_file_types(self):
        processor = self.env["import.processor"].browse()
        file_types = processor._get_file_types()
        expected = [("csv", "CSV"), ("json", "JSON"), ("xlsx", "XLSX"), ("xml", "XML")]
        self.assertEqual(
            file_types, expected, "File types selection does not match definition."
        )

    def test_get_csv_delimiter(self):
        processor = self.env["import.processor"].env["import.processor"].browse()
        delimiters = processor._get_csv_delimiter()
        keys = [d[0] for d in delimiters]
        self.assertListEqual(
            keys, ["comma", "semicolon", "tab"], "CSV Delimiter keys are incorrect."
        )

    def test_get_compression(self):
        processor = self.env["import.processor"].browse()
        compression = processor._get_compression()
        keys = [c[0] for c in compression]
        self.assertListEqual(
            keys, ["zip_one", "zip_all"], "Compression selection keys are incorrect."
        )
