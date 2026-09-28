# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import io

import openpyxl

from odoo.exceptions import UserError

from .common import DataImportCase

HEADER = ["reference", "quantity"]
# A name outside ASCII, so the encoding of the file actually matters.
ROWS = [
    {"reference": "D-001", "quantity": "3"},
    {"reference": "D-002", "quantity": "12"},
]
CSV_TEXT = "reference,quantity\nD-001,3\nD-002,12\n"
LATIN_TEXT = "reference,quantité\nD-001,3\nD-002,12\n"
LATIN_HEADER = ["reference", "quantité"]
LATIN_ROWS = [
    {"reference": "D-001", "quantité": "3"},
    {"reference": "D-002", "quantité": "12"},
]


class TestDataImportReader(DataImportCase):
    def _xlsx_bytes(self):
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.append(HEADER)
        sheet.append(["D-001", 3])
        # Excel hands integers back as floats; the reader must still yield "12".
        sheet.append(["D-002", 12.0])
        stream = io.BytesIO()
        workbook.save(stream)
        return stream.getvalue()

    def test_read_csv_utf8(self):
        log = self._create_log(content=CSV_TEXT.encode("utf-8"))
        self.assertEqual(log._read_rows(), (HEADER, ROWS))

    def test_read_csv_strips_bom(self):
        log = self._create_log(content=CSV_TEXT.encode("utf-8-sig"))
        fieldnames, rows = log._read_rows()
        self.assertEqual(fieldnames, HEADER)
        self.assertEqual(rows, ROWS)

    def test_read_csv_in_another_encoding(self):
        log = self._create_log(
            content=LATIN_TEXT.encode("iso-8859-1"), encoding="iso-8859-1"
        )
        self.assertEqual(log._read_rows(), (LATIN_HEADER, LATIN_ROWS))

    def test_read_csv_wrong_encoding_is_reported(self):
        log = self._create_log(content=LATIN_TEXT.encode("iso-8859-1"))
        with self.assertRaises(UserError):
            log._read_rows()

    def test_read_csv_empty_file(self):
        log = self._create_log(content=b"")
        self.assertEqual(log._read_rows(), ([], []))

    def test_read_xlsx_matches_csv(self):
        log = self._create_log(
            content=self._xlsx_bytes(), file_name="feed.xlsx", file_format="xlsx"
        )
        self.assertEqual(log._read_rows(), (HEADER, ROWS))

    def test_columns_read_by_position_ignore_the_header(self):
        # The header says something else entirely; position is what counts.
        content = b"A,B\nD-001,3\nD-002,12\n"
        log = self._create_log(content=content, column_names="reference\nquantity")
        self.assertEqual(log._read_rows(), (HEADER, ROWS))

    def test_columns_by_position_without_a_header(self):
        content = b"D-001,3\nD-002,12\n"
        log = self._create_log(
            content=content, column_names="reference\nquantity", has_header=False
        )
        self.assertEqual(log._read_rows(), (HEADER, ROWS))

    def test_columns_by_position_in_xlsx(self):
        log = self._create_log(
            content=self._xlsx_bytes(),
            file_name="positional.xlsx",
            file_format="xlsx",
            column_names="reference\nquantity",
        )
        self.assertEqual(log._read_rows(), (HEADER, ROWS))

    def test_blank_rows_are_dropped(self):
        content = b"reference,quantity\nD-001,3\n,\nD-002,12\n"
        log = self._create_log(content=content)
        self.assertEqual(log._read_rows(), (HEADER, ROWS))
