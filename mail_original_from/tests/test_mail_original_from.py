# -*- coding: utf-8 -*-
# Copyright 2017 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import email

from odoo.tests import common
from odoo.tools import decode_message_header


MAIL_MESSAGE = """Return-Path: <support@odoo-community.org>
To: info@odoo-community.org
Received: by mail1.openerp.com (Postfix, from userid 10002)
    id 5DF9ABFB2A; Fri, 10 Aug 2017 16:16:39 +0200 (CEST)
From: support@odoo-community.org
X-Original-From: info@odoo-community.org
Subject: {subject}
MIME-Version: 1.0
Content-Type: multipart/alternative;
    boundary="----=_Part_4200734_24778174.1344608186754"
Date: Fri, 10 Aug 2017 14:16:26 +0000
Message-ID: 123456789
------=_Part_4200734_24778174.1344608186754
Content-Type: text/plain; charset=utf-8
Content-Transfer-Encoding: quoted-printable

Please call me as soon as possible this afternoon!

--
Staff
------=_Part_4200734_24778174.1344608186754
Content-Type: text/html; charset=utf-8
Content-Transfer-Encoding: quoted-printable

<html>
 <head>=20
  <meta http-equiv=3D"Content-Type" content=3D"text/html; charset=3Dutf-8" />
 </head>=20
 <body style=3D"margin: 0; padding: 0; background: #ffffff;">=20

  <p>Please call me as soon as possible this afternoon!</p>

  <p>--<br/>
     Staff
  <p>
 </body>
</html>
------=_Part_4200734_24778174.1344608186754--
"""


class TestMailOriginalFrom(common.TransactionCase):

    def test_01_message_parse(self):
        message = email.message_from_string(MAIL_MESSAGE)
        msg = self.env['mail.thread'].message_parse(message)
        self.assertEqual(msg['email_from'], 'info@odoo-community.org')
        self.assertEqual(msg['from'], 'info@odoo-community.org')

    def test_02_message_route_verify(self):
        msg = email.message_from_string(MAIL_MESSAGE)
        route = ('res.users', 1, None, self.env.uid, '')
        self.env['mail.thread'].message_route_verify(msg, msg, route)
        email_from = decode_message_header(msg, 'From')
        self.assertEqual(email_from, 'info@odoo-community.org')
