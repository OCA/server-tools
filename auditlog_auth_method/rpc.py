# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import contextvars
import functools
import logging

from odoo.http import request

_logger = logging.getLogger(__name__)

RPC_CALL = contextvars.ContextVar("auditlog_auth_method_rpc_call", default=None)
RPC_HTTP = contextvars.ContextVar("auditlog_auth_method_rpc_http", default=None)


def patch_rpc_dispatch():
    from odoo.service import model as service_model

    dispatch = service_model.dispatch
    if getattr(dispatch, "_auditlog_auth_method", False):
        return

    @functools.wraps(dispatch)
    def auditlog_dispatch(method, params):
        try:
            call = (params[0], int(params[1]), params[2])
        except (IndexError, TypeError, ValueError):
            return dispatch(method, params)
        token = RPC_CALL.set(call)
        try:
            return dispatch(method, params)
        finally:
            RPC_CALL.reset(token)

    auditlog_dispatch._auditlog_auth_method = True
    service_model.dispatch = auditlog_dispatch
    _logger.info("PATCHED odoo.service.model.dispatch")


def _get_rpc_http_info():
    if not request:
        return None
    httprequest = request.httprequest
    return {
        "path": httprequest.path,
        "root_url": httprequest.url_root,
        "remote_addr": httprequest.remote_addr,
        "user_agent": httprequest.user_agent.string or False,
        "http_request_ids": {},
    }


def patch_rpc_controller():
    from odoo.addons.base.controllers import rpc as rpc_controller

    dispatch_rpc = rpc_controller.dispatch_rpc
    if getattr(dispatch_rpc, "_auditlog_auth_method", False):
        return

    @functools.wraps(dispatch_rpc)
    def auditlog_dispatch_rpc(service_name, method, params):
        token = RPC_HTTP.set(_get_rpc_http_info())
        try:
            return dispatch_rpc(service_name, method, params)
        finally:
            RPC_HTTP.reset(token)

    auditlog_dispatch_rpc._auditlog_auth_method = True
    rpc_controller.dispatch_rpc = auditlog_dispatch_rpc
    _logger.info("PATCHED odoo.addons.base.controllers.rpc.dispatch_rpc")
