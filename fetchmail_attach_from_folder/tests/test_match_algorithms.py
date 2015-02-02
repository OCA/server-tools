# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 Therp BV (<http://therp.nl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models
from openerp.tests.common import TransactionCase
from openerp.addons.fetchmail_attach_from_folder.match_algorithm import (
    email_exact, email_domain, openerp_standard)


class TestMatchAlgorithms(TransactionCase):
    def do_matching(self, match_algorithm, expected_xmlid, conf, mail_message,
                    mail_message_org=None):
        matcher = match_algorithm()
        matches = matcher.search_matches(
            self.env.cr, self.env.uid, conf, mail_message, mail_message_org)
        self.assertEqual(len(matches), 1)
        self.assertEqual(
            matches[0], self.env.ref(expected_xmlid).id)
        matcher.handle_match(
            self.env.cr, self.env.uid, None, matches[0], conf, mail_message,
            mail_message_org, None)

    def test_email_exact(self):
        mail_message = {
            'subject': 'Testsubject',
            'to': 'demo@yourcompany.example.com',
            'from': 'someone@else.com',
        }
        conf = self.env['fetchmail.server.folder'].browse([models.NewId()])
        conf.model_id = self.env.ref('base.model_res_partner').id
        conf.model_field = 'email'
        conf.match_algorithm = 'email_exact'
        conf.mail_field = 'to,from'
        conf.server_id = self.env['fetchmail.server'].browse([models.NewId()])
        self.do_matching(
            email_exact.email_exact, 'base.user_demo_res_partner',
            conf, mail_message)
        self.assertEqual(
            self.env.ref('base.user_demo_res_partner').message_ids.subject,
            mail_message['subject'])

    def test_email_domain(self):
        mail_message = {
            'subject': 'Testsubject',
            'to': 'test@seagate.com',
            'from': 'someone@else.com',
        }
        conf = self.env['fetchmail.server.folder'].browse([models.NewId()])
        conf.model_id = self.env.ref('base.model_res_partner').id
        conf.model_field = 'email'
        conf.match_algorithm = 'email_domain'
        conf.mail_field = 'to,from'
        conf.use_first_match = True
        conf.server_id = self.env['fetchmail.server'].browse([models.NewId()])
        self.do_matching(
            email_domain.email_domain, 'base.res_partner_address_31',
            conf, mail_message)
        self.assertEqual(
            self.env.ref('base.res_partner_address_31').message_ids.subject,
            mail_message['subject'])

    def test_openerp_standard(self):
        mail_message_org = (
            "To: demo@yourcompany.example.com\n"
            "From: someone@else.com\n"
            "Subject: testsubject\n"
            "Message-Id: 42\n"
            "Hello world"
        )
        conf = self.env['fetchmail.server.folder'].browse([models.NewId()])
        conf.model_id = self.env.ref('base.model_res_partner').id
        conf.model_field = 'email'
        conf.match_algorithm = 'openerp_standard'
        conf.mail_field = 'to,from'
        conf.server_id = self.env['fetchmail.server'].browse([models.NewId()])
        matcher = openerp_standard.openerp_standard()
        matches = matcher.search_matches(
            self.env.cr, self.env.uid, conf, None, mail_message_org)
        self.assertEqual(len(matches), 1)
        matcher.handle_match(
            self.env.cr, self.env.uid, None, matches[0], conf, None,
            mail_message_org, None, None)
        self.assertIn(
            'Hello world',
            self.env['mail.message']
                .search([('subject', '=', 'testsubject')]).body)
