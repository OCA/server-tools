# Copyright 2020 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class IapAccount(models.Model):
    _inherit = ["iap.account", "server.env.mixin"]
    _name = "iap.account"

    name = fields.Char()
    provider = fields.Selection([("odoo", "Odoo IAP")], required=True, default="odoo")

    @property
    def _server_env_fields(self):
        return {
            "provider": {},
            "account_token": {},
        }

    def _get_service_from_provider(self):
        """In case that the provider only propose one service you can
        return the service_name in you module to simplify the user interface"""
        return None

    def _set_service_from_provider(self):
        for record in self:
            service = record._get_service_from_provider()
            if service and record.service_name != service:
                record.service_name = service

    @api.model_create_multi
    def create(self, vals_list):
        record = super().create(vals_list)
        record._set_service_from_provider()
        return record

    def write(self, vals):
        super().write(vals)
        self._set_service_from_provider()
        return True
