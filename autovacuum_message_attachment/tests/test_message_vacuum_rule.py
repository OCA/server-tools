# © 2018 Akretion (Florian da Costa)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date, timedelta

from odoo import api, exceptions
from odoo.tests import common


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
        self.registry.enter_test_mode(self.env.cr)
        self.env = api.Environment(self.registry.test_cr, self.env.uid,
                                   self.env.context)
        self.subtype = self.env.ref('mail.mt_comment')
        self.message_obj = self.env['mail.message']
        self.channel_model = self.env.ref('mail.model_mail_channel')
        today = date.today()
        self.before_400_days = today - timedelta(days=400)

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

    def test_res_model_domain(self):
        partner = self.env['res.partner'].create({'name': 'Test Partner'})
        # automatic creation message
        self.assertEqual(len(partner.message_ids), 1)
        # change date message to simulate it is an old one
        partner.message_ids.write({'date': '2017-01-01'})
        partner_model = self.env.ref('base.model_res_partner')

        rule_vals = {
            'name': 'Partners',
            'retention_time': 399,
            'message_type': 'all',
            'model_ids': [(6, 0, [partner_model.id])],
            'model_filter_domain': "[['name', '=', 'Dummy']]",
            'empty_subtype': True,
        }
        rule = self.env['message.vacuum.rule'].create(rule_vals)
        self.message_obj.autovacuum_mail_message()
        # no message deleted as the filter does not match
        self.assertEqual(len(partner.message_ids), 1)

        rule.write({
            'model_filter_domain': "[['name', '=', 'Test Partner']]"
        })
        self.message_obj.autovacuum_mail_message()
        self.assertEqual(len(partner.message_ids), 0)
