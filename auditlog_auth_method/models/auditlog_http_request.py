# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.http import request

from ..rpc import RPC_CALL, RPC_HTTP


class AuditlogHTTPRequest(models.Model):
    _inherit = "auditlog.http.request"

    remote_addr = fields.Char(string="Client IP", readonly=True)
    user_agent = fields.Char(readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        if request:
            httprequest = request.httprequest
            for vals in vals_list:
                vals.setdefault("remote_addr", httprequest.remote_addr)
                vals.setdefault("user_agent", httprequest.user_agent.string or False)
        return super().create(vals_list)

    @api.model
    def current_http_request(self):
        rpc_http = RPC_HTTP.get()
        if not rpc_http:
            return super().current_http_request()
        return self._get_rpc_http_request(rpc_http)

    @api.model
    def _get_rpc_http_request(self, rpc_http):
        http_request_ids = rpc_http["http_request_ids"]
        dbname = self.env.cr.dbname
        http_request = self.browse(http_request_ids.get(dbname)).exists()
        if http_request:
            return http_request.id
        rpc_call = RPC_CALL.get()
        http_request = self.create(
            {
                "name": rpc_http["path"],
                "root_url": rpc_http["root_url"],
                "user_id": rpc_call[1] if rpc_call else self.env.uid,
                "remote_addr": rpc_http["remote_addr"],
                "user_agent": rpc_http["user_agent"],
            }
        )
        http_request_ids[dbname] = http_request.id
        return http_request.id
