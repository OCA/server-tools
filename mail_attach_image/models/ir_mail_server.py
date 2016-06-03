# -*- coding: utf-8 -*-
# © 2016 Vauxoo - http://www.vauxoo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# info Vauxoo (info@vauxoo.com)
# contributor: Ivan Yelizariev @yelizariev
# coded by: yennifer@vauxoo.com
# planned by: moylop260@vauxoo.com

from email.mime.base import MIMEBase
from email import Encoders
from openerp.addons.base.ir.ir_mail_server import encode_header_param
import base64
import re

from openerp import models


class IrMailServer(models.Model):
    _inherit = 'ir.mail_server'

    def get_images(self, body):
        """Extract of boby template the code base64 image.

        :params string body: email body.
        :returns string new_body: new email body with attach image.
        :returns: list custom_attachments: list of image in code base64"""
        ftemplate = '__image-%s__'
        fcounter = 0
        custom_attachments = []

        pattern = re.compile(r'"data:image/png;base64,[^"]*"')
        pos = 0
        new_body = ''
        while True:
            match = pattern.search(body, pos)
            if not match:
                new_body = body
                break
            start = match.start()
            end = match.end()
            data = body[start + len('"data:image/png;base64,'):end-1]
            new_body += body[pos:start]

            fname = ftemplate % fcounter
            fcounter += 1
            custom_attachments.append((fname, base64.b64decode(data)))

            new_body += '"cid:%s"' % fname
            pos = end

            new_body += body[pos:]
        return new_body, custom_attachments

    def image2attach(self, msg, image_attachments=None):
        """Attach the image in email

        :params msg: email.mime.multipart.MIMEMultipart.
        :params list image_attachments: list of image in code base64.
        """
        if image_attachments is None:
            image_attachments = []
        for (fname, fcontent) in image_attachments:
            filename_rfc2047 = encode_header_param(fname)
            part = MIMEBase('application', "octet-stream")
            part.add_header('Content-ID', '<%s>' % filename_rfc2047)
            part.set_payload(fcontent)
            Encoders.encode_base64(part)
            msg.attach(part)

    def build_email(self, email_from, email_to, subject, body, email_cc=None,
                    email_bcc=None, reply_to=False, attachments=None,
                    message_id=None, references=None, object_id=False,
                    subtype='plain', headers=None, body_alternative=None,
                    subtype_alternative='plain'):
        new_body, image_attachments = self.get_images(body)
        msg = super(IrMailServer, self).build_email(
            email_from, email_to, subject, new_body, email_cc, email_bcc,
            reply_to, attachments, message_id, references, object_id, subtype,
            headers, body_alternative, subtype_alternative)
        self.image2attach(msg, image_attachments)
        return msg
