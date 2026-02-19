# Copyright 2017 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import functools
import math

from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


class TestPartition(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.Category = cls.env["res.partner.category"]
        cls.c1 = cls.Category.create({"name": "c1"})
        cls.c2 = cls.Category.create({"name": "c2"})
        cls.c3 = cls.Category.create({"name": "c3"})

        cls.Partner = cls.env["res.partner"]
        cls.parent1 = cls.Partner.create({"name": "parent1"})
        cls.parent2 = cls.Partner.create({"name": "parent2"})
        cls.child1 = cls.Partner.create({"name": "child1"})
        cls.child2 = cls.Partner.create({"name": "child2"})
        cls.child3 = cls.Partner.create({"name": "child3"})
        cls.x = cls.Partner.create(
            {
                "name": "x",
                "employee": True,
                "category_id": [Command.set([cls.c1.id, cls.c2.id])],
                "child_ids": [Command.set([cls.child1.id, cls.child2.id])],
                "parent_id": cls.parent1.id,
            }
        )
        cls.y = cls.Partner.create(
            {
                "name": "y",
                "employee": False,
                "category_id": [Command.set([cls.c2.id, cls.c3.id])],
                "child_ids": [Command.set([cls.child2.id, cls.child3.id])],
                "parent_id": cls.parent2.id,
            }
        )
        cls.z = cls.Partner.create(
            {
                "name": "z",
                "employee": False,
                "category_id": [Command.set([cls.c1.id, cls.c3.id])],
                "child_ids": [Command.set([cls.child1.id, cls.child3.id])],
                "parent_id": cls.parent2.id,
            }
        )
        cls.xyz = cls.x + cls.y + cls.z

    def test_partition_many2many(self):
        self.partition_field_test("category_id")

    def test_partition_many2one(self):
        self.partition_field_test("parent_id")

    def test_partition_one2many(self):
        self.partition_field_test("child_ids")

    def test_partition_boolean(self):
        self.partition_field_test("employee", relational=False)

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

    def test_partition_lambda(self):
        """Test an arbitrary predicate."""
        partition = (self.c1 | self.c2).partition(lambda c: "2" in c.name)
        self.assertEqual(set(partition.keys()), {True, False})

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

        with mute_logger("odoo.tests.common"):
            records.__class__._default_batch_size = batch_size
        batches_from_default = list(records.batch())
        self.assertEqual(batches_from_default, batches)
        delattr(records.__class__, "_default_batch_size")

    def test_read_per_record(self):
        categories = self.c1 | self.c2 | self.c3
        field_list = ["name"]
        data = categories.read_per_record(field_list)
        self.assertEqual(len(data), len(categories))
        for record in categories:
            self.assertTrue(record.id in data)
            record_data = data[record.id]
            self.assertEqual(list(record_data.keys()), field_list)
