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
from openerp import exceptions


class TestExportSqlQuery(TransactionCase):

    def setUp(self):
        super(TestExportSqlQuery, self).setUp()
        query_vals = {
            'name': 'test',
            'query': "SELECT name, street FROM res_partner;"
        }
        self.sql_model = self.registry('sql.export')
        self.query_id = self.sql_model.create(
            self.cr,
            self.uid,
            query_vals)

    def test_sql_query(self):
        test = self.sql_model.export_sql_query(
            self.cr, self.uid, [self.query_id])
        self.registry('sql.file.wizard').export_sql(
            self.cr, self.uid, test['res_id'])
        wizard = self.registry('sql.file.wizard').browse(
            self.cr, self.uid, test['res_id'])
        export = base64.b64decode(wizard.binary_file)
        self.assertEqual(export.split(';')[0], 'name')
        self.assertTrue(len(export.split(';')) > 6)

    def test_prohibited_queries_creation(self):
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
            with self.assertRaises(exceptions.ValidationError):
                self.sql_model.create(
                    self.cr, self.uid,
                    {'name': 'test_prohibited',
                     'query': query})
        ok_query = {
            'name': 'test ok',
            'query': "SELECT create_date FROM res_partner"
        }
        query_id = self.sql_model.create(self.cr, self.uid, ok_query)
        self.assertIsNotNone(query_id)
