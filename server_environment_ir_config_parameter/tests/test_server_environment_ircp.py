# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from cStringIO import StringIO

from odoo.exceptions import UserError
from odoo.tests import common
from odoo.tools import convert


class TestEnv(common.TransactionCase):

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
        # when creating, the value is overridden by config file
        self.ICP.set_param('ircp_from_config', 'new_value')
        value = self.ICP.get_param('ircp_from_config')
        self.assertEqual(value, 'config_value')
        # when writing, the value is overridden by config file
        res = self.ICP.search([('key', '=', 'ircp_from_config')])
        self.assertEqual(len(res), 1)
        res.write({'value': 'new_value'})
        value = self.ICP.get_param('ircp_from_config')
        self.assertEqual(value, 'config_value')
        # unlink works normally...
        res = self.ICP.search([('key', '=', 'ircp_from_config')])
        self.assertEqual(len(res), 1)
        res.unlink()
        res = self.ICP.search([('key', '=', 'ircp_from_config')])
        self.assertEqual(len(res), 0)
        # but the value is recreated when getting param again
        value = self.ICP.get_param('ircp_from_config')
        self.assertEqual(value, 'config_value')
        res = self.ICP.search([('key', '=', 'ircp_from_config')])
        self.assertEqual(len(res), 1)

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

    def test_override_xmldata(self):
        xml = """<odoo>
            <data>
                <record model="ir.config_parameter" id="some_record_id">
                    <field name="key">ircp_from_config</field>
                    <field name="value">value_from_xml</field>
                </record>
            </data>
        </odoo>"""
        convert.convert_xml_import(self.env.cr, 'testmodule', StringIO(xml))
        value = self.ICP.get_param('ircp_from_config')
        self.assertEqual(value, 'config_value')
