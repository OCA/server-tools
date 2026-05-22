# Copyright 2025 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo_test_helper import FakeModelLoader

from odoo.addons.base.tests.common import BaseCommon


class TestFieldVectorUpdate(BaseCommon):
    def setUp(self):
        res = super().setUp()
        self.loader = FakeModelLoader(self.env, self.__module__)
        self.loader.backup_registry()
        self.addCleanup(self.loader.restore_registry)

        # pylint: disable=import-outside-toplevel
        from .models import TestModel

        self.loader.update_registry([TestModel])

        self.TestModel = self.env[TestModel._name]

        return res

    def test_update_db_column(self):
        self.assertEqual(
            self.TestModel._fields["vector"].get_current_vector_size(
                self.env.cr, self.TestModel._table, "vector"
            ),
            3,
        )
        from .models import TestModelUpgrade

        self.loader.update_registry([TestModelUpgrade])
        self.assertEqual(
            self.TestModel._fields["vector"].get_current_vector_size(
                self.env.cr, self.TestModel._table, "vector"
            ),
            5,
        )
