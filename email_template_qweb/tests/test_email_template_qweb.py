# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.tests.common import TransactionCase


class TestEmailTemplateQweb(TransactionCase):
    def test_email_template_qweb(self):
        template = self.env.ref('email_template_qweb.email_template_demo1')
        mail_values = template.generate_email_batch(
            template.id, [self.env.user.id])
        self.assertTrue(
            # this comes from the called template if everything worked
            '<footer>' in mail_values[self.env.user.id]['body_html'])
