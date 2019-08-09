# -*- coding: utf-8 -*-
# Copyright (C) 2019 Akretion (<http://www.akretion.com>)
# @author: Florian da Costa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase
from openerp.tools import config
from openerp import exceptions


class TestExportSqlQueryExternal(TransactionCase):

    def setUp(self):
        super(TestExportSqlQueryExternal, self).setUp()
        self.sql_report_demo = self.env.ref('sql_export.sql_export_partner')

    def test_sql_queryi_external_database(self):
        # since we can't easily test a query on an external database
        # without mock, we just test that, when the option is checked, the
        # query is executed on a different cursor. Meaning Odoo did
        # successfully opened a new database connection.
        res_sql = self.sql_report_demo._execute_sql_request(mode='fetchall')
        partner_count = len(res_sql)

        self.env['res.partner'].create({'name': 'test'})
        res_sql = self.sql_report_demo._execute_sql_request(mode='fetchall')
        # The partner created on original cursor is present in the new result
        # of the query
        self.assertEqual(len(res_sql), partner_count + 1)

        config['external_db_name'] = self.env.cr.dbname
        self.sql_report_demo.write({'use_external_database': True})
        res_sql = self.sql_report_demo._execute_sql_request(mode='fetchall')
        # The partner created in original cursor is not present because
        # a new cursor has been opened.
        self.assertEqual(len(res_sql), partner_count)

    def test_no_db_in_config_file(self):
        self.sql_report_demo.write({'use_external_database': True})
        with self.assertRaises(exceptions.UserError):
            self.sql_report_demo._execute_sql_request(mode='fetchall')
