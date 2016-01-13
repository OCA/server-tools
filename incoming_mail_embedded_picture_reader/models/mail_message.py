# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import lxml.html as html
from openerp import models, api


class MailMessage(models.Model):
    _inherit = 'mail.message'

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        """
        Search after all "<img>" tags into the body and replace "cid" src
        content with the correct attachment website_url
        """
        res = super(MailMessage, self).create(vals)
        if res.attachment_ids:
            root = html.document_fromstring(res.body)
            for img in root.findall('.//img'):
                src = img.get('src')
                src_cid = src[src.find(':')+1:]
                for attachment in res.attachment_ids:
                    f_name = attachment.name
                    cid = f_name[f_name.find("<")+1:f_name.find('>')]
                    if cid == src_cid:
                        attachment.name = f_name[:f_name.find('<')]
                        img.set('src', attachment._get_image_url())
                        break
            res.body = html.tostring(root)
        return res
