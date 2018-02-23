# -*- coding: utf-8 -*-
# © 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from urllib import urlencode
from lxml.html import document_fromstring
from openerp import _
from openerp.tests.common import HttpCase
from openerp.tools import mute_logger


class UICase(HttpCase):
    def setUp(self):
        super(UICase, self).setUp()
        self.icp = self.env["ir.config_parameter"]
        self.old_allow_uninvited = self.icp.get_param(
            "auth_signup.allow_uninvited")
        self.icp.set_param("auth_signup.allow_uninvited", "True")

        # Workaround https://github.com/odoo/odoo/issues/12237
        self.cr.commit()

        self.data = {
            "csrf_token": self.csrf_token(),
            "name": "Somebody",
        }
        self.msg = {
            "badmail": _("That does not seem to be an email address."),
            "failure": _(
                "Something went wrong, please try again later or contact us."),
            "success": _("Check your email to activate your account!"),
        }

    def tearDown(self):
        """Workaround https://github.com/odoo/odoo/issues/12237."""
        super(UICase, self).tearDown()
        self.icp.set_param(
            "auth_signup.allow_uninvited", self.old_allow_uninvited)
        self.cr.commit()

    def html_doc(self, url="/web/signup", data=None, timeout=10):
        """Get an HTML LXML document."""
        if data:
            data = bytes(urlencode(data))
        return document_fromstring(self.url_open(url, data, timeout).read())

    def csrf_token(self):
        """Get a valid CSRF token."""
        doc = self.html_doc()
        return doc.xpath("//input[@name='csrf_token']")[0].get("value")

    def search_text(self, doc, text):
        """Search for any element containing the text."""
        return doc.xpath("//*[contains(text(), '%s')]" % text)

    def test_bad_email(self):
        """Test rejection of bad emails."""
        self.data["login"] = "bad email"
        doc = self.html_doc(data=self.data)
        self.assertTrue(self.search_text(doc, self.msg["badmail"]))

    @mute_logger("openerp.addons.mail.models.mail_mail")
    @mute_logger("openerp.addons.auth_signup_verify_email.controllers.main")
    def test_good_email(self):
        """Test acceptance of good emails.

        This test could lead to success if your SMTP settings are correct, or
        to failure otherwise. Any case is expected, since tests usually run
        under unconfigured demo instances.
        """
        self.data["login"] = "good@example.com"
        doc = self.html_doc(data=self.data)
        self.assertTrue(
            self.search_text(doc, self.msg["failure"]) or
            self.search_text(doc, self.msg["success"]))
