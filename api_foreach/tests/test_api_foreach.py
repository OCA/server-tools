# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api
from odoo.tests.common import TransactionCase


class TestRecordset(object):
    """ It provides a mock recordset for testing foreach api """

    records = ['test1', 'test2']

    def __iter__(self):
        for record in self.records:
            yield record

    @api.foreach
    def decorated_method(self):
        """ It provides a method decorated with foreach """
        return self


class TestApiForeach(TransactionCase):

    def setUp(self):
        super(TestApiForeach, self).setUp()
        self.count = 0

    def test_api_monkey_patch(self):
        """ It should monkey-patch api.foreach into odoo.api """
        self.assertTrue(
            callable(api.foreach),
        )

    def test_api_iterate(self):
        """ It should iterate and return list of method results """
        res = TestRecordset().decorated_method()
        self.assertEqual(
            res, TestRecordset.records,
        )

    def test_api_foreach_append_all(self):
        """ It should add ``foreach`` to ``__all__`` of ``odoo.api`` """
        self.assertIn('foreach', api.__all__)
