# -*- coding: utf-8 -*-
# © 2016  Vauxoo (<http://www.vauxoo.com/>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import os
from logging.handlers import BufferingHandler

from openerp.tests import common
from openerp.tools.convert import convert_file

_logger = logging.getLogger(__name__)


class TestHandler(BufferingHandler):
    """Logging handler to get the logger messages
    """

    def emit(self, record):
        """Append logging message record to `self.buffer`
        """
        self.buffer.append(record.__dict__)


class TestConvertFile(common.TransactionCase):
    """Test convert_file method patched
    """

    def setUp(self):
        super(TestConvertFile, self).setUp()
        self.module = os.path.basename(
            os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        self.handler = TestHandler(0)
        self.imd_logger = logging.getLogger(
            'openerp.addons.%s.models.ir_model_data' % self.module)
        self.imd_logger.addHandler(self.handler)
        self.imd = self.env['ir.model.data']
        self.imm = self.env['ir.module.module']
        self.fdemo = 'demo/partner_category_demo.xml'
        self.fdata = 'data/partner_category_data.xml'
        self.fdata2 = 'data/partner_category_data2.xml'
        self.funachiev = 'data/partner_category_unachievable_data.xml'
        self.funachiev2 = 'data/partner_category_unachievable_data2.xml'
        self.msg_demo_ref_from_data = (
            u"Demo xml_id 'res_partner_category_demo_01' of '" + self.module +
            "/demo/partner_category_demo.xml' is referenced from data xml '" +
            self.module + "/data/%s'")
        self.msg_xmlid_unachievable = (u"The xml_id '%s' is unachievable.")

    def tearDown(self):
        super(TestConvertFile, self).tearDown()
        self.imd.clear_caches()
        self.imm.clear_caches()
        self.imd_logger.removeHandler(self.handler)
        self.handler.close()

    def get_logs(self, levelno=None):
        levelno = logging.WARNING if levelno is None else levelno
        return [
            log['message'] for log in self.handler.buffer
            if log['levelno'] == levelno]

    def create_imd(self, filename, kind, rows_expected=None,
                   msgs_expected=None, module=None):
        """Create ir.model.data record from `convert_file` method.

        :param filename str: File name to import.
        :param kind str: Category of information (data, demo, test)
        :param rows_expected int: Number of records expected.
        :param msgs_expected int: Number of logger messages expected.
        :param module str: Name of module to import filename.
            default self.module
        :return: ir.model.data browse with records created.
        """
        if module is None:
            module = self.module
        imd_before = self.imd.search([('module', '=', module)])
        convert_file(self.cr, module, filename, None, kind=kind)
        imd_after = self.imd.search([('module', '=', module)])
        imd_new = (imd_after - imd_before)
        if rows_expected is not None:
            self.assertEqual(len(imd_new), rows_expected)
        if msgs_expected is not None:
            logs = self.get_logs()
            self.assertEqual(len(logs), msgs_expected)
        return imd_new

    def test_10_demo_ref_from_data(self):
        """Test demo referenced from data
        """
        self.create_imd(self.fdemo, 'demo', 1, 0)
        self.create_imd(self.fdata, 'data', 1, 1)
        msg_expected = self.msg_demo_ref_from_data % \
            'partner_category_data.xml'
        self.assertEqual(self.get_logs()[0], msg_expected)

    def test_20_demo_overwritten_from_data(self):
        """Test demo overwritten from data
        """
        self.create_imd(self.fdemo, 'demo', 1, 0)
        self.create_imd(self.fdata2, 'data', 0, 1)
        msg_expected = self.msg_demo_ref_from_data % \
            'partner_category_data2.xml'
        self.assertEqual(self.get_logs()[0], msg_expected)

    def test_30_xml_id_ref_unachievable(self):
        """Test a xml_id referenced unachievable
        """
        imd_new = self.create_imd(self.fdemo, 'data', 1, 0)
        imd_new.write({'module': 'unachievable'})
        imd_new = self.create_imd(self.funachiev, 'data', 1, 1)
        msg_expected = self.msg_xmlid_unachievable % \
            'unachievable.res_partner_category_demo_01'
        self.assertEqual(self.get_logs()[0], msg_expected)

    def test_40_xml_id_overwritten_unachievable(self):
        """Test a xml_id overwritten unachievable
        """
        imd_new = self.create_imd(self.fdemo, 'data', 1, 0)
        self.imm.search([('name', '=', self.module)], limit=1).copy({
            'name': 'unachievable', 'state': 'installed', 'auto_install': False
        })
        imd_new.write({'module': 'unachievable'})
        self.create_imd(self.funachiev2, 'data', 0, 1)
        msg_expected = self.msg_xmlid_unachievable % \
            'unachievable.res_partner_category_demo_01'
        self.assertEqual(self.get_logs()[0], msg_expected)

    def test_50_xml_id_ref_achievable(self):
        """Test a xml_id referenced unachievable directly but achievable by
        a module 'auto_install'
        """
        imd_new = self.create_imd(self.fdemo, 'data', 1, 0)
        self.assertFalse(self.handler.buffer)
        self.imm.search([('name', '=', self.module)], limit=1).copy({
            'name': 'unachievable', 'state': 'installed', 'auto_install': True
        })
        imd_new.write({'module': 'unachievable'})
        self.create_imd(self.funachiev, 'data', 1, 0)

    def test_60_xml_id_overwritten_achievable(self):
        """Test a xml_id overwritten unachievable directly but achievable by
        a module 'auto_install'
        """
        imd_new = self.create_imd(self.fdemo, 'data', 1, 0)
        self.imm.search([('name', '=', self.module)], limit=1).copy({
            'name': 'unachievable', 'state': 'installed', 'auto_install': True
        })
        imd_new.write({'module': 'unachievable'})
        self.create_imd(self.funachiev2, 'data', 0, 0)
