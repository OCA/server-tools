# Copyright (C) 2023 Therp (<http://www.therp.nl>).
# @author Tom Blauwendraat <tblauwendraat@therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from math import floor

from odoo_test_helper import FakeModelLoader

from odoo.tests.common import SavepointCase


class TestOrderByRelated(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from .fake_models import FakeCustomer

        cls.loader.update_registry((FakeCustomer,))

        # Create test data
        cls.countries = []
        cls.countries.append(
            cls.env["res.country"].create(
                {
                    "name": "A-land",
                    "code": "Q1",
                }
            )
        )
        cls.countries.append(
            cls.env["res.country"].create(
                {
                    "name": "B-land",
                    "code": "Q2",
                }
            )
        )
        cls.customers = cls.env["fake.customer"]
        for c in range(16):
            # Customers with some weird keys to sort on
            customer = cls.env["fake.customer"].create(
                {
                    "name": "Customer %d" % (c,),
                    "sortkey1": floor(c / 8),  # 0,0...0,1,1...1
                    "country_id": cls.countries[floor(c / 8)].id,
                    "sortkey2": c,  # 0,1,2,.......15
                    "sortkey3": (c + 3) % 16,  # 3,4,...15,0,1,2
                }
            )
            cls.customers |= customer

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super().tearDownClass()

    def test_1_sort_by_related(self):
        """Test if we can now search by non-stored related fields"""
        result = self.env["fake.customer"].search([], order="country_name asc")
        self.assertEqual(result[8:15].mapped("country_id"), self.countries[1])
        result = self.env["fake.customer"].search([], order="country_name desc")
        self.assertEqual(result[8:15].mapped("country_id"), self.countries[0])
        # same-model related field
        result = self.env["fake.customer"].search([], order="fake_sortkey3 asc")
        self.assertEqual(result[0], self.customers[13])

    def test_2_sortable(self):
        """Test if the fields show as sortable"""
        fields_get = self.env["fake.customer"].fields_get()
        self.assertTrue(fields_get["country_code"]["sortable"])
        self.assertTrue(fields_get["country_name"]["sortable"])

    def test_3_sort_by_two_related_fields(self):
        self.env["fake.customer"].search(
            [], order="country_code asc, country_name desc"
        )

    def test_4_sort_by_mix_of_fields(self):
        customers = self.customers
        # country_name bychance is also a translated field, so also test that.
        result = self.env["fake.customer"].search(
            [], order="country_name desc, sortkey2 asc"
        )
        self.assertEqual(result[0], customers[8])
        result = self.env["fake.customer"].search(
            [], order="sortkey2 asc, country_code asc"
        )
        self.assertEqual(result[0], customers[0])
        result = self.env["fake.customer"].search(
            [], order="sortkey1 desc, sortkey3 asc, country_code asc"
        )
        self.assertEqual(result[0], customers[13])
