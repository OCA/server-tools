# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import functools
from odoo.tests.common import TransactionCase


class TestPartition(TransactionCase):
    def setUp(self):
        super(TestPartition, self).setUp()

        self.Category = self.env["res.partner.category"]
        self.c1 = self.Category.create({"name": "c1"})
        self.c2 = self.Category.create({"name": "c2"})
        self.c3 = self.Category.create({"name": "c3"})

        self.Partner = self.env['res.partner']
        self.parent1 = self.Partner.create({"name": "parent1"})
        self.parent2 = self.Partner.create({"name": "parent2"})
        self.child1 = self.Partner.create({"name": "child1"})
        self.child2 = self.Partner.create({"name": "child2"})
        self.child3 = self.Partner.create({"name": "child3"})
        self.x = self.Partner.create({
            "name": "x",
            "customer": True,
            "category_id": [(6, 0, [self.c1.id, self.c2.id])],
            "child_ids": [(6, 0, [self.child1.id, self.child2.id])],
            "parent_id": self.parent1.id,
        })
        self.y = self.Partner.create({
            "name": "y",
            "customer": False,
            "category_id": [(6, 0, [self.c2.id, self.c3.id])],
            "child_ids": [(6, 0, [self.child2.id, self.child3.id])],
            "parent_id": self.parent2.id,
        })
        self.z = self.Partner.create({
            "name": "z",
            "customer": False,
            "category_id": [(6, 0, [self.c1.id, self.c3.id])],
            "child_ids": [(6, 0, [self.child1.id, self.child3.id])],
            "parent_id": self.parent2.id,
        })
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
