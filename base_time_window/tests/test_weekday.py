# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.fields import Date
from odoo.tests.common import TransactionCase


class TestWeekday(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        time_weekday_mapping = dict(cls.env["time.weekday"]._fields["name"].selection)
        for val, name in time_weekday_mapping.items():
            setattr(
                cls,
                name.lower(),
                cls.env["time.weekday"].search([("name", "=", val)], limit=1),
            )

    def test_next_weekday_date(self):
        # 2024-01-01 is Monday, next Monday (including date_from) is 2024-01-01
        self.assertEqual(
            self.monday._get_next_weekday_date(Date.to_date("2024-01-01")),
            Date.to_date("2024-01-01"),
        )
        # 2024-01-01 is Monday, next Monday (excluding date_from) is 2024-01-08
        self.assertEqual(
            self.monday._get_next_weekday_date(
                Date.to_date("2024-01-01"), include_date_from=False
            ),
            Date.to_date("2024-01-08"),
        )
        # 2024-01-01 is Monday, next Tuesday is 2024-01-02
        self.assertEqual(
            self.tuesday._get_next_weekday_date(Date.to_date("2024-01-01")),
            Date.to_date("2024-01-02"),
        )
        # 2024-01-01 is Monday, next Wednesday is 2024-01-03
        self.assertEqual(
            self.wednesday._get_next_weekday_date(Date.to_date("2024-01-01")),
            Date.to_date("2024-01-03"),
        )
        # 2024-01-01 is Monday, next Thursday is 2024-01-04
        self.assertEqual(
            self.thursday._get_next_weekday_date(Date.to_date("2024-01-01")),
            Date.to_date("2024-01-04"),
        )
        # 2024-01-01 is Monday, next Friday is 2024-01-05
        self.assertEqual(
            self.friday._get_next_weekday_date(Date.to_date("2024-01-01")),
            Date.to_date("2024-01-05"),
        )
        # 2024-01-01 is Monday, next Saturday is 2024-01-06
        self.assertEqual(
            self.saturday._get_next_weekday_date(Date.to_date("2024-01-01")),
            Date.to_date("2024-01-06"),
        )
        # 2024-01-01 is Monday, next Sunday is 2024-01-07
        self.assertEqual(
            self.sunday._get_next_weekday_date(Date.to_date("2024-01-01")),
            Date.to_date("2024-01-07"),
        )
