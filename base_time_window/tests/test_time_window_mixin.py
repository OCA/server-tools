from odoo_test_helper import FakeModelLoader

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestTimeWindowMixin(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from .test_models import TestTimeWindowModel

        cls.loader.update_registry((TestTimeWindowModel,))

        cls.customer1 = cls.env["res.partner"].create({"name": "Test1"})
        cls.customer2 = cls.env["res.partner"].create({"name": "Test2"})
        cls.customer3 = cls.env["res.partner"].create({"name": "Test3"})

        cls.weekday1 = cls.env["time.weekday"].search([("name", "=", "1")])
        cls.weekday2 = cls.env["time.weekday"].search([("name", "=", "2")])

    def test_time_window_no_overlap(self):
        with self.assertRaises(ValidationError):
            self.record1 = self.env["test.time.window.model"].create(
                {
                    "partner_id": self.customer1.id,
                    "time_window_start": 9.0,
                    "time_window_end": 12.0,
                }
            )

        with self.assertRaises(ValidationError):
            self.env["test.time.window.model"].create(
                {
                    "partner_id": self.customer2.id,
                    "time_window_start": 15.0,
                    "time_window_end": 13.0,
                    "time_window_weekday_ids": self.weekday1.ids,
                }
            )

        self.record2 = self.env["test.time.window.model"].create(
            {
                "partner_id": self.customer3.id,
                "time_window_start": 13.0,
                "time_window_end": 15.0,
                "time_window_weekday_ids": self.weekday1.ids,
            }
        )
        self.assertTrue(self.record2)

        with self.assertRaises(ValidationError):
            self.record3 = self.env["test.time.window.model"].create(
                {
                    "partner_id": self.customer3.id,
                    "time_window_start": 15.0,
                    "time_window_end": 25.0,
                    "time_window_weekday_ids": self.weekday1.ids,
                }
            )

        with self.assertRaises(ValidationError):
            self.record4 = self.env["test.time.window.model"].create(
                {
                    "partner_id": self.customer3.id,
                    "time_window_start": 0.998,
                    "time_window_end": 22.0,
                    "time_window_weekday_ids": self.weekday1.ids,
                }
            )

        with self.assertRaises(ValidationError):
            self.record5 = self.env["test.time.window.model"].create(
                {
                    "partner_id": self.customer3.id,
                    "time_window_start": 25,
                    "time_window_end": 22.0,
                    "time_window_weekday_ids": self.weekday1.ids,
                }
            )
