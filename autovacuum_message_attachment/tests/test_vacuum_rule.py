# © 2018 Akretion (Florian da Costa)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
from datetime import date, timedelta

from odoo import api, exceptions
from odoo.tests import common
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class TestVacuumRule(common.TransactionCase):
    def create_mail_message(self, message_type, subtype):
        vals = {
            "message_type": message_type,
            "subtype_id": subtype and subtype.id or False,
            "date": self.before_400_days,
            "model": "res.partner",
            "res_id": self.env.ref("base.partner_root").id,
            "subject": "Test",
            "body": "Body Test",
        }
        return self.message_obj.create(vals)

    def tearDown(self):
        self.registry.leave_test_mode()
        super(TestVacuumRule, self).tearDown()

    def setUp(self):
        super(TestVacuumRule, self).setUp()
        self.registry.enter_test_mode()
        self.env = api.Environment(
            self.registry.test_cr, self.env.uid, self.env.context
        )
        self.subtype = self.env.ref("mail.mt_comment")
        self.message_obj = self.env["mail.message"]
        self.attachment_obj = self.env["ir.attachment"]
        self.partner_model = self.env.ref("base.model_res_partner")
        today = date.today()
        self.before_400_days = today - timedelta(days=400)

    def test_mail_vacuum_rules(self):
        rule_vals = {
            "name": "Subtype Model",
            "ttype": "message",
            "retention_time": 399,
            "message_type": "email",
            "model_ids": [(6, 0, [self.env.ref("base.model_res_partner").id])],
            "message_subtype_ids": [(6, 0, [self.subtype.id])],
        }
        rule = self.env["vacuum.rule"].create(rule_vals)
        m1 = self.create_mail_message("notification", self.subtype)
        m2 = self.create_mail_message("email", self.env.ref("mail.mt_note"))
        m3 = self.create_mail_message("email", False)
        message_ids = [m1.id, m2.id, m3.id]
        self.message_obj.autovacuum(ttype="message")
        message = self.message_obj.search([("id", "in", message_ids)])
        # no message deleted because either message_type is wrong or subtype
        # is wrong or subtype is empty
        self.assertEqual(len(message), 3)

        rule.write({"message_type": "notification", "retention_time": 405})
        self.message_obj.autovacuum(ttype="message")
        message = self.message_obj.search([("id", "in", message_ids)])
        # no message deleted because of retention time
        self.assertEqual(len(message), 3)
        rule.write({"retention_time": 399})
        self.message_obj.autovacuum(ttype="message")
        message = self.message_obj.search([("id", "in", message_ids)])

        self.assertEqual(len(message), 2)

        rule.write(
            {
                "message_type": "email",
                "message_subtype_ids": [(6, 0, [])],
                "empty_subtype": True,
            }
        )
        self.message_obj.autovacuum(ttype="message")
        message = self.message_obj.search([("id", "in", message_ids)])
        self.assertEqual(len(message), 0)

    def create_attachment(self, name):
        vals = {
            "name": name,
            "datas": base64.b64encode(b"Content"),
            "datas_fname": name,
            "res_id": self.env.ref("base.partner_root").id,
            "res_model": "res.partner",
        }
        return self.env["ir.attachment"].create(vals)

    def test_attachment_vacuum_rule(self):
        rule_vals = {
            "name": "Partner Attachments",
            "ttype": "attachment",
            "retention_time": 100,
            "model_ids": [(6, 0, [self.partner_model.id])],
            "filename_pattern": "test",
        }
        self.env["vacuum.rule"].create(rule_vals)
        a1 = self.create_attachment("Test-dummy")
        a2 = self.create_attachment("test24")
        # Force create date to old date to test deletion with 100 days
        # retention time
        before_102_days = date.today() - timedelta(days=102)
        before_102_days_str = before_102_days.strftime(
            DEFAULT_SERVER_DATE_FORMAT
        )
        self.env.cr.execute(
            """
            UPDATE ir_attachment SET create_date = '%s'
            WHERE id = %s
        """
            % (before_102_days_str, a2.id)
        )
        a2.write({"create_date": date.today() - timedelta(days=102)})
        a3 = self.create_attachment("other")
        self.env.cr.execute(
            """
            UPDATE ir_attachment SET create_date = '%s'
            WHERE id = %s
        """
            % (before_102_days_str, a3.id)
        )
        attachment_ids = [a1.id, a2.id, a3.id]
        self.attachment_obj.autovacuum(ttype="attachment")
        attachments = self.attachment_obj.search(
            [("id", "in", attachment_ids)]
        )
        # Only one message deleted because other 2 are with bad name or to
        # recent.
        self.assertEqual(len(attachments), 2)

    def test_retention_time_constraint(self):
        rule_vals = {
            "name": "Subtype Model",
            "ttype": "message",
            "retention_time": 0,
            "message_type": "email",
        }
        with self.assertRaises(exceptions.ValidationError):
            self.env["vacuum.rule"].create(rule_vals)

    def test_res_model_domain(self):
        partner = self.env["res.partner"].create({"name": "Test Partner"})
        # automatic creation message
        self.assertEqual(len(partner.message_ids), 1)
        # change date message to simulate it is an old one
        partner.message_ids.write({"date": "2017-01-01"})
        partner_model = self.env.ref("base.model_res_partner")

        rule_vals = {
            "name": "Partners",
            "ttype": "message",
            "retention_time": 399,
            "message_type": "all",
            "model_ids": [(6, 0, [partner_model.id])],
            "model_filter_domain": "[['name', '=', 'Dummy']]",
            "empty_subtype": True,
        }
        rule = self.env["vacuum.rule"].create(rule_vals)
        self.message_obj.autovacuum(ttype="message")
        # no message deleted as the filter does not match
        self.assertEqual(len(partner.message_ids), 1)

        rule.write({"model_filter_domain": "[['name', '=', 'Test Partner']]"})
        self.message_obj.autovacuum(ttype="message")
        self.assertEqual(len(partner.message_ids), 0)
