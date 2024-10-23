# Copyright 2022 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    @api.model
    def _get_tracked_fields(self, updated_fields):
        fields_per_models = self.env["ir.model"]._get_custom_tracked_fields_per_model()
        if self._name in fields_per_models:
            return self.fields_get(fields_per_models[self._name])
        else:
            return super()._get_tracked_fields(updated_fields)
