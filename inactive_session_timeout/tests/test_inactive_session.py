# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

from odoo.tests import common
from ..models.res_users import DELAY_KEY
import time


class TestInactiveSession(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestInactiveSession, cls).setUpClass()
        cls.ipm = cls.env['ir.config_parameter']
        cls.rus = cls.env['res.users']
        cls.db = common.get_db_name()

    def test_01_timeout(self):
        """ Test timeout after delay """
        self.ipm.set_param(DELAY_KEY, 1)
        res = self.rus.authenticate(self.db, 'admin', 'admin', {})
        time.sleep(1.1)
        res = self.rus.browse(res).check(self.db, res, 'admin')
