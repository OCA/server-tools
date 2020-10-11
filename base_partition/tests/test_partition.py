# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import functools
import math

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestPartition(TransactionCase):
    def setUp(self):
        super(TestPartition, self).setUp()

        self.Category = self.env["res.partner.category"]
        self.c1 = self.Category.create({"name": "c1"})
        self.c2 = self.Category.create({"name": "c2"})
        self.c3 = self.Category.create({"name": "c3"})

        self.Partner = self.env["res.partner"]
        self.parent1 = self.Partner.create({"name": "parent1"})
        self.parent2 = self.Partner.create({"name": "parent2"})
        self.child1 = self.Partner.create({"name": "child1"})
        self.child2 = self.Partner.create({"name": "child2"})
        self.child3 = self.Partner.create({"name": "child3"})
        self.x = self.Partner.create(
            {
                "name": "x",
                "customer": True,
                "category_id": [(6, 0, [self.c1.id, self.c2.id])],
                "child_ids": [(6, 0, [self.child1.id, self.child2.id])],
                "parent_id": self.parent1.id,
            }
        )
        self.y = self.Partner.create(
            {
                "name": "y",
                "customer": False,
                "category_id": [(6, 0, [self.c2.id, self.c3.id])],
                "child_ids": [(6, 0, [self.child2.id, self.child3.id])],
                "parent_id": self.parent2.id,
            }
        )
        self.z = self.Partner.create(
            {
                "name": "z",
                "customer": False,
                "category_id": [(6, 0, [self.c1.id, self.c3.id])],
                "child_ids": [(6, 0, [self.child1.id, self.child3.id])],
                "parent_id": self.parent2.id,
            }
        )
        self.xyz = self.x + self.y + self.z

    def test_partition_many2many(self):
        self.partition_field_test("category_id")

    def test_partition_many2one(self):
        self.partition_field_test("parent_id")

    def test_partition_one2many(self):
        self.partition_field_test("child_ids")

    def test_partition_boolean(self):
        self.partition_field_test("customer", relational=False)

    def test_partition_dotdot_relational(self):
        self.partition_field_test("parent_id.category_id", relational=True, dotdot=True)

    def test_partition_dotdot_nonrelational(self):
        self.partition_field_test("parent_id.name", relational=False, dotdot=True)

    def partition_field_test(self, field_name, relational=True, dotdot=False):
        """To check that we have a partition we need to check that:
           - all field values are keys
           - the set of all keys is the same
        """
        partition = self.xyz.partition(field_name)

        if relational:
            values = [s.mapped(field_name) for s in self.xyz]
        else:
            values = self.xyz.mapped(field_name)
        if dotdot and not relational:
            values = [str(s.mapped(field_name)) for s in self.xyz]
        self.assertEqual(set(partition.keys()), set(values))

        records = functools.reduce(sum, partition.values())
        self.assertEqual(self.xyz, records)  # we get the same recordset

    def test_batch(self):
        """The sum of all batches should be the original recordset;
           an empty recordset should return no batch;
           without a batch parameter, the model's _default_batch_size should be used.
        """
        records = self.xyz
        batch_size = 2

        assert len(records)  # only makes sense with nonempty recordset
        batches = list(records.batch(batch_size))
        self.assertEqual(len(batches), math.ceil(len(records) / batch_size))
        for batch in batches[:-1]:
            self.assertEqual(len(batch), batch_size)
        last_batch_size = len(records) % batch_size or batch_size
        self.assertEqual(len(batches[-1]), last_batch_size)
        self.assertEqual(functools.reduce(sum, batches), records)

        empty_recordset = records.browse()
        no_batches = list(empty_recordset.batch(batch_size))
        self.assertEqual(no_batches, [])

        with self.assertRaises(UserError):
            list(records.batch())

        records.__class__._default_batch_size = batch_size
        batches_from_default = list(records.batch())
        self.assertEqual(batches_from_default, batches)

    def test_read_per_record(self):
        categories = self.c1 | self.c2 | self.c3
        field_list = ["name"]
        data = categories.read_per_record(field_list)
        self.assertEqual(len(data), len(categories))
        for record in categories:
            self.assertTrue(record.id in data)
            record_data = data[record.id]
            self.assertEqual(list(record_data.keys()), field_list)

    def test_filtered_domain(self):
        """Initially yo satisfy the coverage tools, this test actually documents
           a number of pitfalls of filtered_domain and the differences with a search.
           Commented examples would cause warnings, and even though these are edge-cases
           these behaviours should be known.
        """

        records = self.xyz
        empty_recordset = records.browse()

        def filtered_search(domain):
            search = self.xyz.search(domain)
            return search.filtered(lambda r: r.id in self.xyz.ids)

        self.assertEqual(records, records.filtered_domain([]))
        self.assertEqual(empty_recordset, records.filtered_domain([(0, "=", 1)]))

        for field in ["name"]:
            for r in self.xyz:
                domain = [(field, "=", r[field])]
                self.assertEqual(self.xyz.filtered_domain(domain), r)
                self.assertEqual(filtered_search(domain), r)

                domain = [(field, "in", r[field])]
                self.assertTrue(self.xyz.filtered_domain(domain), r)
                with self.assertRaises(ValueError):
                    filtered_search(domain)

        for field in ["customer"]:
            for r in [self.x, self.y | self.z]:
                value = r[0][field]
                domain = [(field, "=", value)]
                self.assertEqual(self.xyz.filtered_domain(domain), r)
                self.assertEqual(filtered_search(domain), r)
                # domain = [(field, "in", value)]
                # self.assertEqual(self.xyz.filtered_domain(domain), r)
                # expected_result = r if value else empty_recordset  # !
                # self.assertEqual(filtered_search(domain), expected_result)

        for field in ["parent_id"]:
            for r in [self.x, self.y | self.z]:
                domain = [(field, "=", r[0][field].id)]
                self.assertEqual(self.xyz.filtered_domain(domain), r)
                self.assertEqual(filtered_search(domain), r)
                domain = [(field, "in", r[0][field].ids)]
                self.assertEqual(self.xyz.filtered_domain(domain), r)
                self.assertEqual(filtered_search(domain), r)

        for r in self.xyz:
            field = "category_id"
            in_domain = [(field, "in", r[field].ids)]
            self.assertEqual(self.xyz.filtered_domain(in_domain), self.xyz)
            self.assertEqual(self.xyz.search(in_domain), self.xyz)
            # eq_domain = [(field, "=", r[field].ids)]
            # self.assertEqual(self.xyz.search(eq_domain), self.xyz)
            # self.assertEqual(self.xyz.filtered_domain(eq_domain), empty_recordset)
