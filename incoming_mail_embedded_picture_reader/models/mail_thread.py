# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re
from openerp import models

RE_CID = re.compile(ur'[^<>]+')


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _get_attachment_data(self, filename, part):
        res = super(MailThread, self)._get_attachment_data(filename, part)
        content_id = part.get('content-id')
        if content_id:
            match = RE_CID.search(content_id)
            if match:
                return ('%s<%s>' % (filename, match.group(0)), res[1])
        return res
