# -*- coding: utf-8 -*-
# © 2016 Vauxoo - http://www.vauxoo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# info Vauxoo (info@vauxoo.com)
# contributor: Ivan Yelizariev @yelizariev
# coded by: yennifer@vauxoo.com
# planned by: moylop260@vauxoo.com

import base64
import os

from lxml import html

from openerp.tests import common


class TestAttachImageEmail(common.TransactionCase):
    # Pseudo-constructor method of the setUp test.
    def setUp(self):
        # Define global variables to test methods.
        super(TestAttachImageEmail, self).setUp()

        self.mail_server = self.env['ir.mail_server'].create({
            'name': 'Test',
            'smtp_host': 'smtp.gmail.com',
        })
        self.logo_b64 = self.env.user.company_id.logo.strip('\n')
        curr_dir = os.path.dirname(os.path.realpath(__file__))
        self.template_html = open(
            os.path.join(curr_dir, "template.html")).read()

    # Test methods
    def test_10_create_attach_image(self):
        """Test verifies that the image was attached properly by comparing
        the last attachment in a message with the code of the image on the
        html template.
        """
        email_from = 'partner1@example.com'
        email_to = 'partner2@example.com'
        subject = 'Test attach image'
        body = self.template_html.format(image_base64=self.logo_b64)
        msg = self.mail_server.build_email(email_from, email_to, subject, body)

        image_attach = msg._payload[-1]
        self.assertEquals(
            image_attach.get_payload().strip('\n'), self.logo_b64)

        email_html_str = base64.decodestring(msg._payload[0].get_payload())
        content = html.document_fromstring(email_html_str)
        image = content.xpath('//table/tbody//img')[0]
        self.assertEquals(image.attrib['src'], 'cid:__image-0__')
