# -*- coding: utf-8 -*-
# © 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from urllib import urlencode
from mock import patch
from lxml.html import document_fromstring
from odoo.tests.common import at_install, post_install, HttpCase
from odoo.addons.mail.models import mail_template


@at_install(False)
@post_install(True)
class UICase(HttpCase):
    def setUp(self):
        super(UICase, self).setUp()
        with self.cursor() as http_cr:
            http_env = self.env(http_cr)
            http_env["ir.config_parameter"].set_param(
                "auth_signup.allow_uninvited", "True")
        self.data = {
            "csrf_token": self.csrf_token(),
            "name": "Somebody",
        }

    def html_doc(self, url="/web/signup", data=None, timeout=30):
        """Get an HTML LXML document."""
        if data:
            data = bytes(urlencode(data))
        with patch(mail_template.__name__ + ".MailTemplate.send_mail"):
            result = self.url_open(url, data, timeout)
        return document_fromstring(result.read())

    def csrf_token(self):
        """Get a valid CSRF token."""
        doc = self.html_doc()
        return doc.xpath("//input[@name='csrf_token']")[0].get("value")

    def test_bad_email(self):
        """Test rejection of bad emails."""
        self.data["login"] = "bad email"
        doc = self.html_doc(data=self.data)
        self.assertTrue(doc.xpath('//p[@class="alert alert-danger"]'))

    def test_good_email(self):
        """Test acceptance of good emails."""
        self.data["login"] = "good@example.com"
        doc = self.html_doc(data=self.data)
        self.assertTrue(doc.xpath('//p[@class="alert alert-success"]'))
