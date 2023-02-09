# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from freezegun import freeze_time

from odoo.tests.common import Form, TransactionCase


class TestIrSequenceDateRangePreviewStandard(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @freeze_time("2001-02-01")
    def test_ir_sequence_date_range_preview(self):
        """Create an ir.sequence record."""
        seq = self.env["ir.sequence"].create(
            {
                "code": "test_date_range_preview",
                "name": "Test date_range preview",
                "use_date_range": True,
                "prefix": "test-%(range_y)s/%(range_month)s/%(range_day)s-",
                "suffix": "-%(range_y)s/%(range_month)s/%(range_day)s",
                "padding": 4,
                "date_range_ids": [
                    (
                        0,
                        0,
                        {
                            "date_from": "2001-01-01",
                            "date_to": "2001-12-31",
                            "number_next_actual": 314,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "date_from": "2002-01-01",
                            "date_to": "2002-12-31",
                            "number_next_actual": 42,
                        },
                    ),
                ],
            }
        )
        self.assertEqual(seq.date_range_ids[0].preview, "test-01/01/01-0314-01/01/01")
        self.assertEqual(seq.date_range_ids[1].preview, "test-02/01/01-0042-02/01/01")

        # Check change sequence padding, preview should change too
        with Form(seq) as s:
            s.padding = 5
            s.implementation = "no_gap"
        self.assertEqual(seq.date_range_ids[0].preview, "test-01/01/01-00314-01/01/01")
        self.assertEqual(seq.date_range_ids[1].preview, "test-02/01/01-00042-02/01/01")
        next_number = seq.date_range_ids[0]._next()
        self.assertEqual(next_number, "test-01/02/01-00314-01/02/01")
