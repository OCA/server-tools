# Copyright 2025 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
import numpy as np
from psycopg2.extensions import AsIs

from odoo.orm.model_classes import add_to_registry

from odoo.addons.base.tests.common import BaseCommon

from ..fields import VectorValue


class TestFieldVector(BaseCommon):
    @classmethod
    def setUpClass(cls):
        res = super().setUpClass()

        # pylint: disable=import-outside-toplevel
        from .models import TestModel

        add_to_registry(cls.registry, TestModel)
        cls.registry._setup_models__(cls.env.cr, ["vector.model"])
        cls.registry.init_models(
            cls.env.cr,
            ["vector.model"],
            {"models_to_check": True},
        )
        cls.addClassCleanup(cls.registry.__delitem__, "vector.model")

        cls.TestModel = cls.env[TestModel._name]

        return res

    def test_create_from_tuple(self):
        record = self.TestModel.create({"vector": (1, 2, 3)})
        self.assertListEqual([1, 2, 3], record.vector.to_list())

    def test_create_from_list(self):
        record = self.TestModel.create({"vector": [1, 2, 3]})
        self.assertListEqual([1, 2, 3], record.vector.to_list())

    def test_create_autopad(self):
        record = self.TestModel.create({"vector": [1, 2]})
        self.assertListEqual([1, 2, 0], record.vector.to_list())

    def test_create_no_autopad(self):
        with self.assertRaisesRegex(
            ValueError,
            "Invalid vector dimensions",
        ):
            self.TestModel.create({"no_autopad": [1, 2]})

        record = self.TestModel.create({"no_autopad": [1, 2, 3]})
        self.assertListEqual([1, 2, 3], record.no_autopad.to_list())

    def test_from_db(self):
        record = self.TestModel.create({"vector": [1, 2, 3]})
        record.flush_recordset()
        record.invalidate_model()
        new_record = self.TestModel.browse(record.id)
        val = new_record.vector
        self.assertIsInstance(val, VectorValue)
        self.assertEqual(val.to_list(), [1, 2, 3])

    def test_plain_sql_select(self):
        record = self.TestModel.create({"vector": [1, 2, 3]})
        record.flush_recordset()
        self.env.cr.execute(
            "SELECT vector FROM %s WHERE id = %s",
            (
                AsIs(record._table),
                record.id,
            ),
        )
        val = self.env.cr.fetchone()[0]
        # Even if we use plain SQL, the value is still a VectorValue
        # because of the adapter registered for the vector type
        # in the database.
        self.assertIsInstance(val, VectorValue)
        self.assertEqual(val.to_list(), [1, 2, 3])

    def test_plain_sql_write(self):
        record = self.TestModel.create({"vector": [1, 2, 3]})
        record.flush_recordset()
        # as VectorValue
        self.env.cr.execute(
            "UPDATE %s SET vector = %s WHERE id = %s",
            (
                AsIs(record._table),
                VectorValue([4, 5, 6]),
                record.id,
            ),
        )
        record.invalidate_model()
        new_record = self.TestModel.browse(record.id)
        val = new_record.vector
        self.assertIsInstance(val, VectorValue)
        self.assertEqual(val.to_list(), [4, 5, 6])

        # as list
        self.env.cr.execute(
            "UPDATE %s SET vector = %s WHERE id = %s",
            (
                AsIs(record._table),
                [7, 8, 9],
                record.id,
            ),
        )
        record.invalidate_model()
        new_record = self.TestModel.browse(record.id)
        val = new_record.vector
        self.assertIsInstance(val, VectorValue)
        self.assertEqual(val.to_list(), [7, 8, 9])

        # as numpy array
        self.env.cr.execute(
            "UPDATE %s SET vector = %s WHERE id = %s",
            (
                AsIs(record._table),
                np.array([10, 11, 12]),
                record.id,
            ),
        )
        record.invalidate_model()
        new_record = self.TestModel.browse(record.id)
        val = new_record.vector
        self.assertIsInstance(val, VectorValue)
        self.assertEqual(val.to_list(), [10, 11, 12])

    def test_write(self):
        record = self.TestModel.create({"vector": [1, 2, 3]})
        record.flush_recordset()
        record.vector = [4, 5, 6]
        value = record.vector
        self.assertIsInstance(value, VectorValue)
        self.assertEqual(value.to_list(), [4, 5, 6])
        record.flush_recordset()
        record.invalidate_model()
        new_record = self.TestModel.browse(record.id)
        self.assertEqual(new_record.vector.to_list(), [4, 5, 6])
        record.vector = np.array([7, 8, 9])
        value = record.vector
        self.assertIsInstance(value, VectorValue)
        self.assertEqual(value.to_list(), [7, 8, 9])

    def test_read(self):
        record = self.TestModel.create({"vector": [1, 2, 3]})
        record.flush_recordset()
        record.invalidate_model()
        new_record = self.TestModel.browse(record.id)
        val = new_record.read(["vector"])[0]["vector"]
        self.assertEqual(val, [1, 2, 3])
