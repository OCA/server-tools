# Copyright 2024 sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestTimeWeekday(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.time_weekday = cls.env["time.weekday"]
        cls.time_weekday_saturday = cls.time_weekday.search([("name", "=", "5")])

    def test_weekday_delete(cls):
        cls.time_weekday._get_id_by_name(cls.time_weekday_saturday.name)
        cls.time_weekday_saturday.unlink()
