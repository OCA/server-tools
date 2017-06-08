# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mail_footer_notified_partners,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mail_footer_notified_partners is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     mail_footer_notified_partners is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with mail_footer_notified_partners.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from anybox.testing.openerp import SharedSetupTransactionCase


class TestMailNotification(SharedSetupTransactionCase):

    def setUp(self):
        super(TestMailNotification, self).setUp()

        self.mail_notification_obj = self.env['mail.notification']
        self.partner_obj = self.env['res.partner']

        self.registry('ir.model').clear_caches()
        self.registry('ir.model.data').clear_caches()

    def test_get_signature_footer(self):

        vals = {
            'name': 'p1@exemple.com',
            'notify_email': 'none',
        }
        partner1 = self.partner_obj.create(vals)
        vals = {
            'name': 'p2@exemple.com',
            'notify_email': 'always',
        }
        partner2 = self.partner_obj.create(vals)
        footer = self.mail_notification_obj.get_signature_footer(self.env.uid)
        self.assertFalse(
            partner1.name in footer or partner2.name in footer,
            'Standard behavior does not add notified partners into the footer')

        footer = self.mail_notification_obj.with_context(
            partners_to_notify=[partner1.id, partner2.id]
        ).get_signature_footer(self.env.uid)

        self.assertFalse(
            partner1.name in footer,
            'Partner with "notify_email: "none" should not be into the footer')
        self.assertTrue(
            partner2.name in footer,
            'Partner with "notify_email: "always" should be into the footer')
