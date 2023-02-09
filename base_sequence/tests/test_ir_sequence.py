# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from freezegun import freeze_time

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestBaseSequence(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_ir_sequence_invalid(self):
        """Create an ir.sequence record with invalid prefix/suffix."""
        seq = self.env["ir.sequence"].create(
            {
                "code": "test_invalid",
                "name": "Test invalid",
                "use_date_range": False,
                "prefix": "test-%(invalid)s-",
            }
        )
        self.assertTrue(seq)

        with self.assertRaises(UserError):
            self.env["ir.sequence"].next_by_code("test_invalid")

        seq.prefix = None
        seq.suffix = "-%(invalid)s"

        with self.assertRaises(UserError):
            self.env["ir.sequence"].next_by_code("test_invalid")

    @freeze_time("2001-02-01")
    def test_ir_sequence_preview(self):
        """Create an ir.sequence record."""
        seq = (
            self.env["ir.sequence"]
            .with_context(ir_sequence_date="2001-02-01")
            .create(
                {
                    "code": "test_preview",
                    "name": "Test preview",
                    "use_date_range": False,
                    "prefix": "test-%(year)s/%(y)s/%(month)s/%(day)s-",
                    "suffix": "-%(year)s/%(y)s/%(month)s/%(day)s",
                    "padding": 4,
                    "number_next_actual": 42,
                }
            )
        )
        self.assertEqual(len(seq), 1)
        self.assertEqual(seq.preview, "test-2001/01/02/01-0042-2001/01/02/01")
