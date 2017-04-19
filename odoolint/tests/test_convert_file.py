# -*- coding: utf-8 -*-
# © 2016  Vauxoo (<http://www.vauxoo.com/>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import os

from openerp.tests import common
from openerp.tools.convert import convert_file

_logger = logging.getLogger(__name__)
MODULE = os.path.basename(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
LOGGER_WORK = 'openerp.addons.%s.models.ir_model_data' % MODULE


class TestFilter(logging.Filter):
    """Class to add the record logging filtered in `self.buffer`
    and don't show it
    """

    def __init__(self):
        super(TestFilter, self).__init__()
        self.buffer = []

    def filter(self, record):
        self.buffer.append(record.__dict__)


class TestConvertFile(common.TransactionCase):
    """Test convert_file method patched
    """

    def setUp(self):
        super(TestConvertFile, self).setUp()
        self.imd_logger = logging.getLogger(LOGGER_WORK)
        self.logger_filter = TestFilter()
        self.imd_logger.addFilter(self.logger_filter)
        self.imd = self.env['ir.model.data']
        self.imm = self.env['ir.module.module']
        self.fdemo = 'demo/partner_category_demo.xml'
        self.fdata = 'data/partner_category_data.xml'
        self.fdata2 = 'data/partner_category_data2.xml'
        self.funachiev = 'data/partner_category_unreachable_data.xml'
        self.funachiev2 = 'data/partner_category_unreachable_data2.xml'
        self.msg_demo_ref_from_data = (
            u"Demo xml_id 'res_partner_category_demo_01' of '" + MODULE +
            "/demo/partner_category_demo.xml' is referenced from data xml '" +
            MODULE + "/data/%s'")
        self.msg_xmlid_unreachable = (u"The xml_id '%s' is unreachable.")

    def tearDown(self):
        super(TestConvertFile, self).tearDown()
        self.imd.clear_caches()
        self.imm.clear_caches()
        self.imd_logger.removeFilter(self.logger_filter)

    def get_logs(self, levelno=None):
        levelno = logging.WARNING if levelno is None else levelno
        return [
            log.get('msg') % log.get('args')
            for log in self.logger_filter.buffer
            if log['levelno'] == levelno]

    def create_imd(self, filename, kind, rows_expected=None,
                   msgs_expected=None, module=None):
        """Create ir.model.data record from `convert_file` method.

        :param filename str: File name to import.
        :param kind str: Category of information (data, demo, test)
        :param rows_expected int: Number of records expected.
        :param msgs_expected int: Number of logger messages expected.
        :param module str: Name of module to import filename.
            default MODULE
        :return: ir.model.data browse with records created.
        """
        if module is None:
            module = MODULE
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

    def create_unreachable(self, old_xmlid, new_xml_id=None, new_module=None,
                           auto_install=None):
        """Create a xml_id valid but unreachable
        """
        if new_module is None:
            new_module = 'unreachable'
        if new_xml_id is None:
            new_xml_id = old_xmlid.split('.')[1]
        self.imm.search([('name', '=', MODULE)], limit=1).copy({
            'name': new_module, 'state': 'installed',
            'auto_install': auto_install})
        unreachable = self.imd.search([
            ('name', '=', old_xmlid.split('.')[1]),
            ('module', '=', old_xmlid.split('.')[0])], limit=1).copy({
                'name': new_xml_id, 'module': new_module})
        return unreachable

    def test_05_auto_install_dependencies(self):
        """Test get `auto_install` dependencies"""
        web_rep = self.imm.search([('name', '=', 'website_report'),
                                   ('auto_install', '=', True)], limit=1)
        self.assertTrue(web_rep)
        web_rep_deps = web_rep.dependencies_id.mapped('depend_id')
        self.assertTrue(web_rep_deps)
        autoinstall_satisfied = web_rep_deps.get_autoinstall_satisfied()
        self.assertIn(web_rep.name,
                      self.imm.browse(autoinstall_satisfied).mapped('name'))

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

    def test_30_ref_unreachable(self):
        """Test a xml_id referenced unreachable
        """
        imd_new = self.create_imd(self.fdemo, 'data', 1, 0)
        self.create_unreachable(imd_new.module + '.' + imd_new.name)
        imd_new = self.create_imd(self.funachiev, 'data', 1, 1)
        msg_expected = self.msg_xmlid_unreachable % \
            'unreachable.res_partner_category_demo_01'
        self.assertEqual(self.get_logs()[0], msg_expected)

    def test_40_overwritten_unreachable(self):
        """Test a xml_id overwritten unreachable
        """
        imd_new = self.create_imd(self.fdemo, 'data', 1, 0)
        self.create_unreachable(imd_new.module + '.' + imd_new.name)
        self.create_imd(self.funachiev2, 'data', 0, 1)
        msg_expected = self.msg_xmlid_unreachable % \
            'unreachable.res_partner_category_demo_01'
        self.assertEqual(self.get_logs()[0], msg_expected)

    def test_50_ref_reachable(self):
        """Test a xml_id referenced unreachable directly but reachable by
        a module 'auto_install'
        """
        imd_new = self.create_imd(self.fdemo, 'data', 1, 0)
        self.create_unreachable(imd_new.module + '.' + imd_new.name,
                                auto_install=True)
        self.create_imd(self.funachiev, 'data', 1, 0)

    def test_60_overwritten_reachable(self):
        """Test a xml_id overwritten unreachable directly but reachable by
        a module 'auto_install'
        """
        imd_new = self.create_imd(self.fdemo, 'data', 1, 0)
        self.create_unreachable(imd_new.module + '.' + imd_new.name,
                                auto_install=True)
        self.create_imd(self.funachiev2, 'data', 0, 0)

    def test_70_ref_unreachable_csv(self):
        """Test a xml_id referenced unreachable
        """
        self.create_unreachable('base.group_user')
        self.create_imd('security/ir.model.access.csv', 'data', 2, 1)
