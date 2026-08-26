# Copyright 2025 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo_test_helper import FakeModelLoader

from odoo.tests.common import TransactionCase


class TestFloatNullable(TransactionCase):
    @classmethod
    def setUpClass(cls):
        res = super().setUpClass()
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        cls.addClassCleanup(cls.loader.restore_registry)

        # pylint: disable=import-outside-toplevel
        from .test_model import TestFloatNullableModel

        cls.loader.update_registry([TestFloatNullableModel])

        cls.test_model = cls.env[TestFloatNullableModel._name]

        return res

    def _get_db_storage_value(self, record, field_name):
        query = f"SELECT {field_name} FROM test_float_nullable WHERE id = %s"
        self.env.cr.execute(query, (record.id,))
        db_value = self.env.cr.fetchone()[0]
        return db_value

    def test_null_handling(self):
        """Test that NULL values are properly handled"""
        self.record_empty = self.test_model.create(
            {
                "name": "Empty Test",
                "value_float_nullable": None,
                "value_float": None,
            }
        )

        self.assertIsNone(self.record_empty.value_float_nullable)
        self.assertFalse(self.record_empty.value_float_nullable == 0.0)
        self.assertTrue(self.record_empty.value_float == 0.0)
        self.assertFalse(self.record_empty.value_float is None)
        # check db storage value
        self.assertIsNone(
            self._get_db_storage_value(self.record_empty, "value_float_nullable")
        )

        self.assertFalse(
            self._get_db_storage_value(self.record_empty, "value_float_nullable") == 0.0
        )
        self.assertTrue(
            self._get_db_storage_value(self.record_empty, "value_float") is not None
        )
        self.assertTrue(
            self._get_db_storage_value(self.record_empty, "value_float") == 0.0
        )

    def test_zero_handling(self):
        """Test that explicit zero is preserved"""
        self.record_zero = self.test_model.create(
            {
                "name": "Zero Test",
                "value_float_nullable": 0.0,
                "value_float": 0.0,
            }
        )
        self.assertFalse(self.record_zero.value_float_nullable is None)
        self.assertTrue(self.record_zero.value_float_nullable == 0.0)
        self.assertTrue(self.record_zero.value_float == 0.0)
        self.assertFalse(self.record_zero.value_float is None)
        # check db storage value
        self.assertTrue(
            self._get_db_storage_value(self.record_zero, "value_float_nullable") == 0.0
        )
        self.assertTrue(
            self._get_db_storage_value(self.record_zero, "value_float_nullable")
            is not None
        )
        self.assertTrue(
            self._get_db_storage_value(self.record_zero, "value_float") is not None
        )
        self.assertTrue(
            self._get_db_storage_value(self.record_zero, "value_float") == 0.0
        )

    def test_number_handling(self):
        """Test with regular numbers"""
        self.record_number = self.test_model.create(
            {
                "name": "Number Test",
                "value_float_nullable": 42.5,
                "value_float": 42.5,
            }
        )
        self.assertEqual(self.record_number.value_float_nullable, 42.5)
        self.assertEqual(self.record_number.value_float, 42.5)
