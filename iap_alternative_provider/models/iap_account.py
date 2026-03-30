# Copyright 2020 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class IapAccount(models.Model):
    _inherit = "iap.account"

    provider = fields.Selection([("odoo", "Odoo IAP")], required=True, default="odoo")

    def _get_service_from_provider(self):
        """In case that the provider only propose one service you can
        return the service in your module to simplify the user interface"""
        return None

    def _set_service_from_provider(self):
        for record in self:
            service = record._get_service_from_provider()
            if service and record.service_id != service:
                record.service_id = service

    @api.onchange("provider")
    def onchange_provider(self):
        self._set_service_from_provider()

    @api.model_create_multi
    def create(self, vals_list):
        record = super().create(vals_list)
        record._set_service_from_provider()
        return record

    def write(self, vals):
        res = super().write(vals)
        self._set_service_from_provider()
        return res
