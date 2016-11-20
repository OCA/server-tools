# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.exceptions import UserError
from openerp.tests import common


class TestEnv(common.SavepointCase):

    def setUp(self):
        super(TestEnv, self).setUp()
        self.ICP = self.env['ir.config_parameter']

    def test_get_param(self):
        """ Get system parameter from config """
        # it's not in db
        res = self.ICP.search([('key', '=', 'ircp_from_config')])
        self.assertFalse(res)
        # read so it's created in db
        value = self.ICP.get_param('ircp_from_config')
        self.assertEqual(value, 'config_value')
        # now it's in db
        res = self.ICP.search([('key', '=', 'ircp_from_config')])
        self.assertEqual(len(res), 1)
        self.assertEqual(res.value, 'config_value')

    def test_set_param_1(self):
        """ We can't set parameters that are in config file """
        # create
        with self.assertRaises(UserError):
            self.ICP.set_param('ircp_from_config', 'new_value')
        # read so it's created in db
        self.ICP.get_param('ircp_from_config')
        # write
        res = self.ICP.search([('key', '=', 'ircp_from_config')])
        self.assertEqual(len(res), 1)
        with self.assertRaises(UserError):
            res.write({'ircp_from_config': 'new_value'})
        # unlink
        with self.assertRaises(UserError):
            res.unlink()

    def test_set_param_2(self):
        """ We can set parameters that are not in config file """
        self.ICP.set_param('some.param', 'new_value')
        self.assertEqual(self.ICP.get_param('some.param'), 'new_value')
        res = self.ICP.search([('key', '=', 'some.param')])
        res.unlink()
        res = self.ICP.search([('key', '=', 'some.param')])
        self.assertFalse(res)

    def test_empty(self):
        """ Empty config values cause error """
        with self.assertRaises(UserError):
            self.ICP.get_param('ircp_empty')
        self.assertEqual(self.ICP.get_param('ircp_nonexistant'), False)
