# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api
from odoo.tests.common import TransactionCase


class TestApiForeach(TransactionCase):

    def test_api_monkey_patch(self):
        """ It should monkey-patch api.foreach into odoo.api """
        self.assertTrue(
            callable(api.foreach),
        )
