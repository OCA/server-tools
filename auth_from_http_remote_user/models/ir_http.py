# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

import openerp
from openerp import models
from openerp import http

from ..utils import REMOTE_USER_HEADER

_logger = logging.getLogger(__name__)


class IrHttp(models.Model):

    _inherit = "ir.http"

    def _authenticate(self, auth_method="user"):
        """Check the HTTP remote user matches the session user.

        This method is invoked for every HTTP request.
        """
        res = super(IrHttp, self)._authenticate(auth_method=auth_method)
        headers = http.request.httprequest.headers.environ
        remote_login = headers.get(REMOTE_USER_HEADER, None)
        session = http.request.session
        if (
            remote_login
            and session
            and session.login
            and remote_login != session.login
        ):
            _logger.warning(
                "Remote user '%s' does not match session user '%s'. "
                "Terminating session.",
                remote_login,
                session.login,
            )
            session.logout(keep_db=True)
            raise openerp.exceptions.AccessDenied()
        return res
