# Copyright (C) 2024 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.http import request


class Http(models.AbstractModel):
    _inherit = "ir.http"

    def session_info(self):
        session_info = super().session_info()
        session_info.update(
            {
                "is_impersonate_user": request.env.user._is_impersonate_user(),
                "impersonate_from_uid": request.session.impersonate_from_uid,
            }
        )
        return session_info
