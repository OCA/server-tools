# Copyright 2026 Heligrafics Fotogrametria S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo_test_helper import FakeModelLoader

from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSearchDateWindow(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from .models import SearchDateWindowTest

        cls.loader.update_registry((SearchDateWindowTest,))
        cls.Model = cls.env["search.date.window.test"]
        now = fields.Datetime.now()
        today = fields.Date.today()

        def create(name, days):
            date = fields.Datetime.add(now, days=days)
            return cls.Model.create(
                {
                    "name": name,
                    "date_start": date,
                    "date_end": date,
                    "day": fields.Date.add(today, days=days),
                }
            )

        cls.recent = create("recent", -2)
        cls.old = create("old", -10)
        cls.future = create("future", 3)
        cls.all_records = cls.recent | cls.old | cls.future

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super().tearDownClass()

    def _search(self, domain=None, model=None):
        model = model if model is not None else self.Model
        return model.search((domain or []) + [("id", "in", self.all_records.ids)])

    def _search_ids_free(self, domain=None, model=None):
        """Search without an ``id`` condition, which would disable the window."""
        model = model if model is not None else self.Model
        return model.search(domain or []) & self.all_records

    def test_window_by_default(self):
        self.assertEqual(self._search_ids_free(), self.recent)

    def test_id_condition_disables_window(self):
        self.assertEqual(self._search(), self.all_records)

    def test_explicit_lower_bound_disables_past_side(self):
        limit = fields.Datetime.subtract(fields.Datetime.now(), days=30)
        records = self._search_ids_free([("date_start", ">=", limit)])
        self.assertEqual(records, self.recent | self.old)

    def test_explicit_upper_bound_disables_future_side(self):
        limit = fields.Datetime.add(fields.Datetime.now(), days=30)
        records = self._search_ids_free([("date_end", "<=", limit)])
        self.assertEqual(records, self.recent | self.future)

    def test_explicit_upper_bound_keeps_past_side(self):
        limit = fields.Datetime.now()
        records = self._search_ids_free([("date_end", "<", limit)])
        self.assertEqual(records, self.recent)

    def test_context_disables_window(self):
        model = self.Model.with_context(date_window_test=False)
        self.assertEqual(self._search_ids_free(model=model), self.all_records)

    def test_side_without_days_is_not_applied(self):
        with patch.object(type(self.Model), "_date_window_past_days", None):
            self.assertEqual(self._search_ids_free(), self.recent | self.old)
        with patch.object(type(self.Model), "_date_window_future_days", None):
            self.assertEqual(self._search_ids_free(), self.recent | self.future)

    def test_custom_window_size(self):
        with patch.object(type(self.Model), "_date_window_past_days", 30):
            self.assertEqual(self._search_ids_free(), self.recent | self.old)

    def test_date_field(self):
        with patch.multiple(
            type(self.Model),
            _date_window_past_field="day",
            _date_window_future_field="day",
        ):
            self.assertEqual(self._search_ids_free(), self.recent)
            limit = fields.Date.subtract(fields.Date.today(), days=30)
            records = self._search_ids_free([("day", ">=", limit)])
            self.assertEqual(records, self.recent | self.old)

    def test_search_count(self):
        domain = [("name", "in", ["recent", "old", "future"])]
        self.assertEqual(self.Model.search_count(domain), 1)
        model = self.Model.with_context(date_window_test=False)
        self.assertEqual(model.search_count(domain), 3)

    def test_read_group(self):
        domain = [("name", "in", ["recent", "old", "future"])]
        groups = self.Model.read_group(domain, ["name"], ["name"])
        self.assertEqual([group["name"] for group in groups], ["recent"])

    def test_relational_field_access(self):
        self.old.parent_id = self.recent
        self.env.invalidate_all()
        self.assertEqual(self.recent.child_ids, self.old)

    def test_explicit_context_applies_to_relational_field_access(self):
        self.old.parent_id = self.recent
        self.env.invalidate_all()
        recent = self.recent.with_context(date_window_test=True)
        self.assertFalse(recent.child_ids)

    def test_stored_compute_of_old_records_is_invalidated(self):
        self.old.ref_id = self.recent
        self.assertEqual(self.old.ref_name, "recent")
        self.recent.name = "renamed"
        self.env.flush_all()
        self.env.invalidate_all()
        self.assertEqual(self.old.ref_name, "renamed")
