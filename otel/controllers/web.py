import json
import logging
import os

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from odoo import http
from odoo.http import request

from odoo.addons.web.controllers.action import Action
from odoo.addons.web.controllers.dataset import DataSet
from odoo.addons.web.controllers.report import ReportController

from .. import bootstrap, utils

_logger = logging.getLogger(__name__)


def trace_common(span):
    try:
        user_name = request.env["res.users"].browse(request.uid).name
    except Exception:
        user_name = "unknown"
    span.set_attribute("http.route", request.httprequest.path)
    span.set_attribute("http.method", request.httprequest.method)
    span.set_attribute("odoo.db", request.db)
    span.set_attribute("odoo.user_id", request.uid)
    span.set_attribute("odoo.user_name", user_name)  # PII
    span.set_attribute("enduser.id", request.uid)
    span.set_attribute("odoo.pid", os.getpid())


class _Action(Action):
    @http.route()
    def load(self, action_id, context=None):
        if not bootstrap._OTEL_INITIALIZED:
            return super().load(action_id, context=context)
        tracer = trace.get_tracer("odoo.otel.web")
        pctx = utils.extract_context()
        with tracer.start_as_current_span("action.load", context=pctx) as span:
            Actions_sudo = request.env["ir.actions.actions"].sudo()
            try:
                action = Actions_sudo.browse(int(action_id))
            except ValueError:
                try:
                    if "." in action_id:
                        action = request.env.ref(action_id)
                    else:
                        action = Actions_sudo.search(
                            [("path", "=", action_id)], limit=1
                        )
                except Exception:
                    action = False

            trace_common(span)
            span.set_attribute("odoo.action_id", action_id)
            span.set_attribute("odoo.action_name", action.name if action else "unknown")

            try:
                res = super().load(action_id, context=context)
                span.set_status(Status(StatusCode.OK))
                return res
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR))
                raise


class _DataSet(DataSet):
    @http.route()
    def call_kw(self, model, method, args, kwargs):
        if not bootstrap._OTEL_INITIALIZED:
            return super().call_kw(model, method, args, kwargs)
        tracer = trace.get_tracer("odoo.otel.web")
        pctx = utils.extract_context()
        with tracer.start_as_current_span("dataset.call_kw", context=pctx) as span:
            trace_common(span)
            span.set_attribute("odoo.model", model)
            span.set_attribute("odoo.method", method)

            try:
                res = super().call_kw(model, method, args, kwargs)
                span.set_status(Status(StatusCode.OK))
                return res
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR))
                raise

    @http.route()
    def call_button(self, model, method, args, kwargs, path=None):
        if not bootstrap._OTEL_INITIALIZED:
            return super().call_button(model, method, args, kwargs, path=path)
        tracer = trace.get_tracer("odoo.otel.web")
        pctx = utils.extract_context()
        with tracer.start_as_current_span("dataset.call_button", context=pctx) as span:
            trace_common(span)
            span.set_attribute("odoo.model", model)
            span.set_attribute("odoo.method", method)

            try:
                res = super().call_button(model, method, args, kwargs, path=path)
                span.set_status(Status(StatusCode.OK))
                return res
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR))
                raise


class _ReportController(ReportController):
    @http.route()
    def report_download(self, data, context=None, token=None, readonly=True):
        if not bootstrap._OTEL_INITIALIZED:
            return super().report_download(
                data, context=context, token=token, readonly=readonly
            )
        tracer = trace.get_tracer("odoo.otel.web")
        pctx = utils.extract_context()
        with tracer.start_as_current_span("report.download", context=pctx) as span:
            requestcontent = json.loads(data)
            url, type_ = requestcontent[0], requestcontent[1]
            pattern = "/report/pdf/" if type_ == "qweb-pdf" else "/report/text/"
            reportname = url.split(pattern)[1].split("?")[0]
            docids = None
            if "/" in reportname:
                reportname, docids = reportname.split("/")

            trace_common(span)
            span.set_attribute("odoo.report_type", type_)
            span.set_attribute("odoo.report_url", url)  # maybe PII
            span.set_attribute("odoo.report_name", reportname)
            if docids:
                span.set_attribute("odoo.report_docids", docids)

            try:
                res = super().report_download(
                    data, context=context, token=token, readonly=readonly
                )
                span.set_status(Status(StatusCode.OK))
                return res
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR))
                raise
