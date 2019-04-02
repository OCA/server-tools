# -*- coding: utf-8 -*-
# (c) 2019 Anass Ahmed, Katherine Zaoral

# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import models
from odoo.http import request

_logger = logging.getLogger(__name__)


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _authenticate(cls, auth_method='user'):
        res = super(IrHttp, cls)._authenticate(auth_method=auth_method)
        # use session.uid instead of env.user because first requests don't have
        # that and basically bypass our check (if you close the browser in an
        # acitve session, then you open it again after the timeout passed)
        if request and request.session and request.session.uid:
            request.env.user._auth_timeout_check()
        return res
