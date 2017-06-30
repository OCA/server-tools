# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

from odoo.tests import common
from ..models.res_users import DELAY_KEY
import time


class TestInactiveSession(common.HttpCase):

    def setUp(self):
        super(TestInactiveSession, self).setUp()
        with self.registry.cursor() as test_cursor:
            env = self.env(test_cursor)
            self.ipm = env['ir.config_parameter']
            self.rus = env['res.users']
        self.db = common.get_db_name()

    def test_01_timeout(self):
        """ Test timeout after delay """
        self.ipm.set_param(DELAY_KEY, 1)
        self.assertTrue(self.ipm.get_param(DELAY_KEY), 1)
        self.authenticate('admin', 'admin')
        time.sleep(1.1)
        res = self.rus.browse(1).check(self.db, 1, 'admin')
