# -*- coding: utf-8 -*-
# Copyright 2017 Bilbonet - Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).
from odoo.tests import common


class TestBaseExternalImport(common.TransactionCase):

    def setUp(self):
        super(TestBaseExternalImport, self).setUp()
        self.task = self.env.ref(
                            'base_external_import.demo_task_postgresql_users')

    def test_import_run_dbtable_arg(self):
        # It should raise a TypeError if task connectión not in args
        with self.assertRaises(TypeError):
            self.task.import_run(self, ids=None)

    def test_execute_import_return_true(self):
        # It should return true if import the data
        res = self.task.import_run(ids=None)
        self.assertEqual(res, True)

    def test_import_schedule_create(self):
        # It should raise a TypeError if create cron fails
        with self.assertRaises(TypeError):
            self.task.import_schedule(self)
