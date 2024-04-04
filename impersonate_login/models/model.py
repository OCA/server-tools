# Copyright (C) 2024 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.http import request


class BaseModel(models.AbstractModel):
    _inherit = "base"

    @api.model
    def _create(self, data_list):
        if request and request.session.impersonate_from_uid:
            user = self.env["res.users"].browse(request.session.impersonate_from_uid)
            return super(BaseModel, self.with_user(user))._create(data_list)
        return super()._create(data_list)

    def write(self, vals):
        if request and request.session.impersonate_from_uid:
            user = self.env["res.users"].browse(request.session.impersonate_from_uid)
            return super(BaseModel, self.with_user(user)).write(vals)
        return super().write(vals)
