# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Florian da Costa
#    Copyright 2015 Akretion
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distnaributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import base64
from openerp.tests.common import TransactionCase
from openerp.exceptions import Warning as UserError


class TestExportSqlQuery(TransactionCase):

    def setUp(self):
        super(TestExportSqlQuery, self).setUp()
        self.sql_export_obj = self.env['sql.export']
        self.wizard_obj = self.env['sql.file.wizard']
        self.sql_report_demo = self.env.ref('sql_export.sql_export_partner')

    def test_sql_query(self):
        wizard = self.wizard_obj.create({
            'sql_export_id': self.sql_report_demo.id,
        })
        wizard.export_sql()
        export = base64.b64decode(wizard.binary_file)
        self.assertEqual(export.split(';')[0], 'name')
        self.assertTrue(len(export.split(';')) > 6)

    def test_prohibited_queries(self):
        prohibited_queries = [
            "upDaTe res_partner SET name = 'test' WHERE id = 1",
            "DELETE FROM sql_export WHERE name = 'test';",
            "  DELETE FROM sql_export WHERE name = 'test'   ;",
            """DELETE
            FROM
            sql_export
            WHERE name = 'test'
            """,
        ]
        for query in prohibited_queries:
            with self.assertRaises(UserError):
                sql_export = self.sql_export_obj.create({
                    'name': 'test_prohibited',
                    'query': query})
                sql_export.button_clean_check_request()

    def test_authorized_queries(self):
        authorized_queries = [
            "SELECT create_date FROM res_partner",
        ]

        for query in authorized_queries:
            sql_export = self.sql_export_obj.create({
                'name': 'test_authorized',
                'query': query})
            sql_export.button_clean_check_request()
            self.assertEqual(
                sql_export.state, 'sql_valid',
                "%s is a valid request" % (query))
