# -*- coding: utf-8 -*-
# Copyright 2015-2017
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import openerp.tests.common as common
from odoo import exceptions


class TestBaseReportAutoQwebCreate(common.TransactionCase):

    def setUp(self):
        super(TestBaseReportAutoQwebCreate, self).setUp()
        self.report_model = self.env['ir.actions.report.xml']
        self.duplicate_model = self.env['ir.actions.report.xml.duplicate']
        self.view_model = self.env['ir.ui.view']

    def test_creation_html(self):
        report_html = self.report_model.create({
            'name': 'Test 1',
            'model': 'res.partner',
            'report_type': 'qweb-html',
            'report_name': 'test1.report_test',
        })
        report_html.button_create_qweb()
        view_num = self.view_model.search_count(
            [('name', 'ilike', report_html.report_name.split('.')[1]),
             ('type', '=', 'qweb')])
        self.assertNotEqual(view_num, 0, 'There are not related views')
        self.assertEqual(view_num, 1, 'Only one view must be created.')

    def test_creation_duplicate_pdf(self):
        report_pdf = self.report_model.create({
            'name': 'Test 2',
            'model': 'res.partner',
            'report_type': 'qweb-pdf',
            'report_name': 'test2.report_test',
        })
        report_pdf.button_create_qweb()
        view_num = self.view_model.search_count(
            [('name', 'ilike', report_pdf.report_name.split('.')[1]),
             ('type', '=', 'qweb')])
        self.assertNotEqual(view_num, 0, 'There are not related views.')
        self.assertEqual(view_num, 1, 'One view must be created.')
        wizard = self.duplicate_model.with_context(
            active_id=report_pdf.id, model=report_pdf.model).create({
                'suffix': 'copytest',
            })
        wizard.duplicate_report()
        report_pdf_copies = self.report_model.search(
            [('report_name', 'ilike', 'test2_copytest.report_test_copytest')])
        for report_pdf_copy in report_pdf_copies:
            view_num2 = self.view_model.search_count(
                [('name', 'ilike', report_pdf_copy.report_name.split('.')[1]),
                 ('type', '=', 'qweb')])
            self.assertNotEqual(view_num2, 0, 'There are not related views.')
            self.assertEqual(view_num2, view_num,
                             'Same view numbers must have been created.')

    def test_wrong_template_name(self):
        with self.assertRaises(exceptions.Warning):
            self.report_model.create({
                'name': 'Test',
                'model': 'res.partner',
                'report_type': 'qweb-pdf',
                'report_name': 'report_test',
            })
