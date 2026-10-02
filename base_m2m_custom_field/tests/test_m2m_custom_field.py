# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from unittest.mock import patch

from odoo import fields

from odoo.addons.base.tests.common import BaseCommon


class TestMany2manyCustomField(BaseCommon):
    def test_field_class_registered_in_fields_module(self):
        self.assertTrue(hasattr(fields, "Many2manyCustom"))
        self.assertTrue(issubclass(fields.Many2manyCustom, fields.Many2many))

    def test_create_table_defaults_to_true(self):
        self.assertTrue(fields.Many2manyCustom.create_table)

    def test_update_db_called_when_create_table_true(self):
        field = fields.Many2manyCustom()
        self.assertTrue(field.create_table)
        with patch.object(fields.Many2many, "update_db") as mock_super:
            field.update_db(None, None)
            mock_super.assert_called_once_with(None, None)

    def test_update_db_skipped_when_create_table_false(self):
        field = fields.Many2manyCustom()
        field.create_table = False
        with patch.object(fields.Many2many, "update_db") as mock_super:
            field.update_db(None, None)
            mock_super.assert_not_called()
