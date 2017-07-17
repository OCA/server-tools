# -*- coding: utf-8 -*-
# Copyright (C) 2017 Akretion (<http://www.akretion.com>)
# @author: Florian da Costa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase
from openerp import SUPERUSER_ID


class TestExportSqlQueryMail(TransactionCase):

    def setUp(self):
        super(TestExportSqlQueryMail, self).setUp()
        self.sql_report_demo = self.env.ref('sql_export.sql_export_partner')
        self.sql_report_demo.write({'mail_user_ids': [(4, SUPERUSER_ID)]})

    def test_sql_query_create_cron(self):
        self.sql_report_demo.create_cron()
        self.assertTrue(self.sql_report_demo.cron_ids)
        cron = self.sql_report_demo.cron_ids
        self.assertEqual(cron.function, '_run_all_sql_export_for_cron')

    def test_sql_query_mail(self):
        mail_obj = self.env['mail.mail']
        mails = mail_obj.search(
            [('model', '=', 'sql.export'),
             ('res_id', '=', self.sql_report_demo.id)])
        self.assertFalse(mails)
        self.sql_report_demo.send_mail()
        mails = mail_obj.search(
            [('model', '=', 'sql.export'),
             ('res_id', '=', self.sql_report_demo.id)])
        self.assertTrue(mails)
