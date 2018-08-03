# -*- coding: utf-8 -*-
# © 2018 Akretion (Florian da Costa)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date, timedelta

from openerp import api, exceptions
from openerp.tests import common
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class TestMessageVacuumRule(common.TransactionCase):

    def create_mail_message(self, message_type, subtype):
        vals = {
            'message_type': message_type,
            'subtype_id': subtype and subtype.id or False,
            'date': self.before_400_days,
            'model': 'mail.channel',
            'res_id': self.env.ref('mail.channel_all_employees').id,
            'subject': 'Test',
            'body': 'Body Test',
        }
        return self.message_obj.create(vals)

    def tearDown(self):
        self.registry.leave_test_mode()
        super(TestMessageVacuumRule, self).tearDown()

    def setUp(self):
        super(TestMessageVacuumRule, self).setUp()
        self.registry.enter_test_mode()
        self.env = api.Environment(self.registry.test_cr, self.env.uid,
                                   self.env.context)
        self.subtype = self.env.ref('mail.mt_comment')
        self.message_obj = self.env['mail.message']
        self.channel_model = self.env.ref('mail.model_mail_channel')
        today = date.today()
        before_400_days = today - timedelta(days=400)
        self.before_400_days = before_400_days.strftime(
            DEFAULT_SERVER_DATE_FORMAT)

    def test_mail_vacuum_rules(self):
        rule_vals = {
            'name': 'Subtype Model',
            'retention_time': 399,
            'message_type': 'email',
            'model_ids': [(6, 0, [self.channel_model.id])],
            'message_subtype_ids': [(6, 0, [self.subtype.id])],
        }
        rule = self.env['message.vacuum.rule'].create(rule_vals)
        m1 = self.create_mail_message('notification', self.subtype)
        m2 = self.create_mail_message('email', self.env.ref('mail.mt_note'))
        m3 = self.create_mail_message('email', False)
        message_ids = [m1.id, m2.id, m3.id]
        self.message_obj.autovacuum_mail_message()
        message = self.message_obj.search(
            [('id', 'in', message_ids)])
        # no message deleted because either message_type is wrong or subtype
        # is wront or subtype is empty
        self.assertEqual(len(message),
                         3)

        rule.write({'message_type': 'notification', 'retention_time': 405})
        self.message_obj.autovacuum_mail_message()
        message = self.message_obj.search(
            [('id', 'in', message_ids)])
        # no message deleted because of retention time
        self.assertEqual(len(message),
                         3)
        rule.write({'retention_time': 399})
        self.message_obj.autovacuum_mail_message()
        message = self.message_obj.search(
            [('id', 'in', message_ids)])

        self.assertEqual(len(message),
                         2)

        rule.write({'message_type': 'email',
                    'message_subtype_ids': [(6, 0, [])],
                    'empty_subtype': True})
        self.message_obj.autovacuum_mail_message()
        message = self.message_obj.search(
            [('id', 'in', message_ids)])
        self.assertEqual(len(message),
                         0)

    def test_retention_time_constraint(self):
        rule_vals = {
            'name': 'Subtype Model',
            'retention_time': 0,
            'message_type': 'email',
        }
        with self.assertRaises(exceptions.ValidationError):
            self.env['message.vacuum.rule'].create(rule_vals)
