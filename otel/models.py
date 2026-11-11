import os

from opentelemetry import trace
from opentelemetry.trace import SpanKind, Status, StatusCode

from odoo import api, models

from odoo.addons.web.models.models import Base as WebModel

from . import bootstrap


def trace_common(span, records):
    span.set_attribute("odoo.db", records.env.cr.dbname)
    span.set_attribute("odoo.user_id", records.env.uid)
    span.set_attribute("odoo.user_name", records.env.user.name)  # PII
    span.set_attribute("enduser.id", records.env.uid)
    span.set_attribute("odoo.pid", os.getpid())


METHODS_TO_PATCH = set()


def _patch_model(model, method_name, method):
    global METHODS_TO_PATCH
    METHODS_TO_PATCH.add((model, method_name, method))


@api.model_create_multi
def create(self, vals_list):
    if not bootstrap._OTEL_INITIALIZED:
        return _model_create(self, vals_list)
    tracer = trace.get_tracer("odoo.otel.models")
    with tracer.start_as_current_span("model.create", kind=SpanKind.INTERNAL) as span:
        trace_common(span, self)
        span.set_attribute("odoo.model", self._name)

        try:
            res = _model_create(self, vals_list)
            span.set_attribute("odoo.res_ids", str(res.ids))  # maybe truncate?
            span.set_status(Status(StatusCode.OK))
            return res
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR))
            raise


_model_create = models.Model.create
_patch_model(models.Model, "create", create)


def write(self, vals):
    if not bootstrap._OTEL_INITIALIZED:
        return _model_write(self, vals)
    tracer = trace.get_tracer("odoo.otel.models")
    with tracer.start_as_current_span("model.write", kind=SpanKind.INTERNAL) as span:
        trace_common(span, self)
        span.set_attribute("odoo.model", self._name)
        span.set_attribute("odoo.res_ids", str(self.ids))  # maybe truncate?

        try:
            res = _model_write(self, vals)
            span.set_status(Status(StatusCode.OK))
            return res
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR))
            raise


_model_write = models.Model.write
_patch_model(models.Model, "write", write)


def read(self, fields=None, load="_classic_read"):
    if not bootstrap._OTEL_INITIALIZED:
        return _model_read(self, fields=fields, load=load)
    tracer = trace.get_tracer("odoo.otel.models")
    with tracer.start_as_current_span("model.read", kind=SpanKind.INTERNAL) as span:
        trace_common(span, self)
        span.set_attribute("odoo.model", self._name)
        span.set_attribute("odoo.fields", str(fields))
        span.set_attribute("odoo.res_ids", str(self.ids))  # maybe truncate?

        try:
            res = _model_read(self, fields=fields, load=load)
            span.set_status(Status(StatusCode.OK))
            return res
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR))
            raise


_model_read = models.Model.read
_patch_model(models.Model, "read", read)


def unlink(self):
    if not bootstrap._OTEL_INITIALIZED:
        return _model_unlink(self)
    tracer = trace.get_tracer("odoo.otel.models")
    with tracer.start_as_current_span("model.unlink", kind=SpanKind.INTERNAL) as span:
        trace_common(span, self)
        span.set_attribute("odoo.model", self._name)
        span.set_attribute("odoo.res_ids", str(self.ids))  # maybe truncate?

        try:
            res = _model_unlink(self)
            span.set_status(Status(StatusCode.OK))
            return res
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR))
            raise


_model_unlink = models.Model.unlink
_patch_model(models.Model, "unlink", unlink)


# web CRUD methods


@api.model
@api.readonly
def web_search_read(
    self, domain, specification, offset=0, limit=None, order=None, count_limit=None
):
    if not bootstrap._OTEL_INITIALIZED:
        return _model_web_search_read(
            self,
            domain,
            specification,
            offset=offset,
            limit=limit,
            order=order,
            count_limit=count_limit,
        )
    tracer = trace.get_tracer("odoo.otel.models")
    with tracer.start_as_current_span(
        "model.web_search_read", kind=SpanKind.INTERNAL
    ) as span:
        trace_common(span, self)
        span.set_attribute("odoo.model", self._name)
        span.set_attribute("odoo.domain", str(domain))
        span.set_attribute("odoo.specification", str(specification))  # maybe truncate?
        span.set_attribute("odoo.offset", offset)
        if limit:
            span.set_attribute("odoo.limit", limit)
        if order:
            span.set_attribute("odoo.order", order)
        if count_limit:
            span.set_attribute("odoo.count_limit", count_limit)

        try:
            res = _model_web_search_read(
                self,
                domain,
                specification,
                offset=offset,
                limit=limit,
                order=order,
                count_limit=count_limit,
            )
            span.set_attribute("odoo.result_count", len(res))
            span.set_status(Status(StatusCode.OK))
            return res
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR))
            raise


_model_web_search_read = WebModel.web_search_read
_patch_model(WebModel, "web_search_read", web_search_read)


def web_save(self, vals, specification, next_id=None):
    if not bootstrap._OTEL_INITIALIZED:
        return _model_web_save(self, vals, specification, next_id=next_id)
    tracer = trace.get_tracer("odoo.otel.models")
    with tracer.start_as_current_span("model.web_save", kind=SpanKind.INTERNAL) as span:
        trace_common(span, self)
        span.set_attribute("odoo.model", self._name)
        span.set_attribute("odoo.vals", str(vals))  # maybe truncate?
        span.set_attribute("odoo.specification", str(specification))  # maybe truncate?
        if next_id:
            span.set_attribute("odoo.next_id", next_id)

        try:
            res = _model_web_save(self, vals, specification, next_id=next_id)
            span.set_status(Status(StatusCode.OK))
            return res
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR))
            raise


_model_web_save = WebModel.web_save
_patch_model(WebModel, "web_save", web_save)


@api.readonly
def web_read(self, specification):
    if not bootstrap._OTEL_INITIALIZED:
        return _model_web_read(self, specification)
    tracer = trace.get_tracer("odoo.otel.models")
    with tracer.start_as_current_span("model.web_read", kind=SpanKind.INTERNAL) as span:
        trace_common(span, self)
        span.set_attribute("odoo.model", self._name)
        span.set_attribute("odoo.specification", str(specification))  # maybe truncate?

        try:
            res = _model_web_read(self, specification)
            span.set_status(Status(StatusCode.OK))
            return res
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR))
            raise


_model_web_read = WebModel.web_read
_patch_model(WebModel, "web_read", web_read)


@api.model
@api.readonly
def web_read_group(
    self, domain, fields, groupby, limit=None, offset=0, orderby=False, lazy=True
):
    if not bootstrap._OTEL_INITIALIZED:
        return _model_web_read_group(
            self,
            domain,
            fields,
            groupby,
            limit=limit,
            offset=offset,
            orderby=orderby,
            lazy=lazy,
        )
    tracer = trace.get_tracer("odoo.otel.models")
    with tracer.start_as_current_span(
        "model.web_read_group", kind=SpanKind.INTERNAL
    ) as span:
        trace_common(span, self)
        span.set_attribute("odoo.model", self._name)
        span.set_attribute("odoo.domain", str(domain))
        span.set_attribute("odoo.fields", str(fields))  # maybe truncate?
        span.set_attribute("odoo.groupby", str(groupby))  # maybe truncate?
        if limit:
            span.set_attribute("odoo.limit", limit)
        span.set_attribute("odoo.offset", offset)
        if orderby:
            span.set_attribute("odoo.orderby", str(orderby))
        span.set_attribute("odoo.lazy", lazy)

        try:
            res = _model_web_read_group(
                self,
                domain,
                fields,
                groupby,
                limit=limit,
                offset=offset,
                orderby=orderby,
                lazy=lazy,
            )
            span.set_attribute("odoo.result_count", len(res))
            span.set_status(Status(StatusCode.OK))
            return res
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR))
            raise


_model_web_read_group = WebModel.web_read_group
_patch_model(WebModel, "web_read_group", web_read_group)


def onchange(self, values, field_names, fields_spec):
    if not bootstrap._OTEL_INITIALIZED:
        return _model_onchange(self, values, field_names, fields_spec)
    tracer = trace.get_tracer("odoo.otel.models")
    with tracer.start_as_current_span("model.onchange", kind=SpanKind.INTERNAL) as span:
        trace_common(span, self)
        span.set_attribute("odoo.model", self._name)
        span.set_attribute("odoo.values", str(values))  # maybe truncate?
        span.set_attribute("odoo.field_names", str(field_names))
        span.set_attribute("odoo.fields_spec", str(fields_spec))  # maybe truncate?

        try:
            res = _model_onchange(self, values, field_names, fields_spec)
            span.set_status(Status(StatusCode.OK))
            return res
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR))
            raise


_model_onchange = models.Model.onchange
_patch_model(models.Model, "onchange", onchange)


# other Odoo ORM methods


@api.model
@api.readonly
def search_count(self, domain, limit=None):
    if not bootstrap._OTEL_INITIALIZED:
        return _model_search_count(self, domain, limit=limit)
    tracer = trace.get_tracer("odoo.otel.models")
    with tracer.start_as_current_span(
        "model.search_count", kind=SpanKind.INTERNAL
    ) as span:
        trace_common(span, self)
        span.set_attribute("odoo.model", self._name)
        span.set_attribute("odoo.domain", str(domain))
        if limit:
            span.set_attribute("odoo.limit", limit)

        try:
            res = _model_search_count(self, domain, limit=limit)
            span.set_attribute("odoo.result_count", res)
            span.set_status(Status(StatusCode.OK))
            return res
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR))
            raise


_model_search_count = models.Model.search_count
_patch_model(models.Model, "search_count", search_count)


@api.model
@api.readonly
@api.returns("self")
def search(self, domain, offset=0, limit=None, order=None):
    if not bootstrap._OTEL_INITIALIZED:
        return _model_search(self, domain, offset=offset, limit=limit, order=order)
    tracer = trace.get_tracer("odoo.otel.models")
    with tracer.start_as_current_span("model.search", kind=SpanKind.INTERNAL) as span:
        trace_common(span, self)
        span.set_attribute("odoo.model", self._name)
        span.set_attribute("odoo.domain", str(domain))
        span.set_attribute("odoo.offset", offset)
        if limit:
            span.set_attribute("odoo.limit", limit)
        if order:
            span.set_attribute("odoo.order", order)

        try:
            res = _model_search(self, domain, offset=offset, limit=limit, order=order)
            span.set_attribute("odoo.result_count", len(res))
            span.set_attribute("odoo.res_ids", str(res.ids))  # maybe truncate?
            span.set_status(Status(StatusCode.OK))
            return res
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR))
            raise


_model_search = models.Model.search
_patch_model(models.Model, "search", search)


@api.model
@api.readonly
@api.returns("self")
def search_fetch(self, domain, field_names, offset=0, limit=None, order=None):
    if not bootstrap._OTEL_INITIALIZED:
        return _model_search_fetch(
            self, domain, field_names, offset=offset, limit=limit, order=order
        )
    tracer = trace.get_tracer("odoo.otel.models")
    with tracer.start_as_current_span(
        "model.search_fetch", kind=SpanKind.INTERNAL
    ) as span:
        trace_common(span, self)
        span.set_attribute("odoo.model", self._name)
        span.set_attribute("odoo.domain", str(domain))
        span.set_attribute("odoo.field_names", str(field_names))  # maybe truncate?
        span.set_attribute("odoo.offset", offset)
        if limit:
            span.set_attribute("odoo.limit", limit)
        if order:
            span.set_attribute("odoo.order", order)

        try:
            res = _model_search_fetch(
                self, domain, field_names, offset=offset, limit=limit, order=order
            )
            span.set_attribute("odoo.result_count", len(res))
            span.set_status(Status(StatusCode.OK))
            return res
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR))
            raise


_model_search_fetch = models.Model.search_fetch
_patch_model(models.Model, "search_fetch", search_fetch)


@api.model
def name_create(self, name):
    if not bootstrap._OTEL_INITIALIZED:
        return _model_name_create(self, name)
    tracer = trace.get_tracer("odoo.otel.models")
    with tracer.start_as_current_span(
        "model.name_create", kind=SpanKind.INTERNAL
    ) as span:
        trace_common(span, self)
        span.set_attribute("odoo.model", self._name)
        span.set_attribute("odoo.name", name)

        try:
            res = _model_name_create(self, name)
            span.set_attribute("odoo.res_id", res[0])
            span.set_status(Status(StatusCode.OK))
            return res
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR))
            raise


_model_name_create = models.Model.name_create
_patch_model(models.Model, "name_create", name_create)


@api.model
@api.readonly
def name_search(self, name="", args=None, operator="ilike", limit=100):
    if not bootstrap._OTEL_INITIALIZED:
        return _model_name_search(
            self, name=name, args=args, operator=operator, limit=limit
        )
    tracer = trace.get_tracer("odoo.otel.models")
    with tracer.start_as_current_span(
        "model.name_search", kind=SpanKind.INTERNAL
    ) as span:
        trace_common(span, self)
        span.set_attribute("odoo.model", self._name)
        span.set_attribute("odoo.name", name)
        span.set_attribute("odoo.args", str(args))
        span.set_attribute("odoo.operator", operator)
        span.set_attribute("odoo.limit", limit)

        try:
            res = _model_name_search(
                self, name=name, args=args, operator=operator, limit=limit
            )
            span.set_attribute("odoo.result_count", len(res))
            span.set_attribute(
                "odoo.res_ids", str([r[0] for r in res])
            )  # maybe truncate?
            span.set_status(Status(StatusCode.OK))
            return res
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR))
            raise


_model_name_search = models.Model.name_search
_patch_model(models.Model, "name_search", name_search)


@api.model
@api.readonly
def read_group(
    self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True
):
    if not bootstrap._OTEL_INITIALIZED:
        return _model_read_group(
            self,
            domain,
            fields,
            groupby,
            offset=offset,
            limit=limit,
            orderby=orderby,
            lazy=lazy,
        )
    tracer = trace.get_tracer("odoo.otel.models")
    with tracer.start_as_current_span(
        "model.read_group", kind=SpanKind.INTERNAL
    ) as span:
        trace_common(span, self)
        span.set_attribute("odoo.model", self._name)
        span.set_attribute("odoo.domain", str(domain))
        span.set_attribute("odoo.fields", str(fields))  # maybe truncate?
        span.set_attribute("odoo.groupby", str(groupby))  # maybe truncate?
        span.set_attribute("odoo.offset", offset)
        if limit:
            span.set_attribute("odoo.limit", limit)
        if orderby:
            span.set_attribute("odoo.orderby", str(orderby))
        span.set_attribute("odoo.lazy", lazy)

        try:
            res = _model_read_group(
                self,
                domain,
                fields,
                groupby,
                offset=offset,
                limit=limit,
                orderby=orderby,
                lazy=lazy,
            )
            span.set_attribute("odoo.result_count", len(res))
            span.set_status(Status(StatusCode.OK))
            return res
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR))
            raise


_model_read_group = models.Model.read_group
_patch_model(models.Model, "read_group", read_group)


def fetch(self, field_names):
    if not bootstrap._OTEL_INITIALIZED:
        return _model_fetch(self, field_names)
    tracer = trace.get_tracer("odoo.otel.models")
    with tracer.start_as_current_span("model.fetch", kind=SpanKind.INTERNAL) as span:
        trace_common(span, self)
        span.set_attribute("odoo.model", self._name)
        span.set_attribute("odoo.field_names", str(field_names))  # maybe truncate?
        span.set_attribute("odoo.res_ids", str(self.ids))  # maybe truncate?

        try:
            res = _model_fetch(self, field_names)
            span.set_status(Status(StatusCode.OK))
            return res
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR))
            raise


_model_fetch = models.Model.fetch
_patch_model(models.Model, "fetch", fetch)


@api.returns("self")
def copy(self, default=None):
    if not bootstrap._OTEL_INITIALIZED:
        return _model_copy(self, default=default)
    tracer = trace.get_tracer("odoo.otel.models")
    with tracer.start_as_current_span("model.copy", kind=SpanKind.INTERNAL) as span:
        trace_common(span, self)
        span.set_attribute("odoo.model", self._name)
        span.set_attribute("odoo.res_ids", str(self.ids))  # maybe truncate?
        span.set_attribute("odoo.default", str(default))  # maybe truncate?

        try:
            res = _model_copy(self, default=default)
            span.set_attribute("odoo.new_res_ids", str(res.ids))  # maybe truncate?
            span.set_status(Status(StatusCode.OK))
            return res
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR))
            raise


_model_copy = models.Model.copy
_patch_model(models.Model, "copy", copy)


@api.model
@api.readonly
def search_read(
    self, domain=None, fields=None, offset=0, limit=None, order=None, **read_kwargs
):
    if not bootstrap._OTEL_INITIALIZED:
        return _model_search_read(
            self,
            domain=domain,
            fields=fields,
            offset=offset,
            limit=limit,
            order=order,
            **read_kwargs,
        )
    tracer = trace.get_tracer("odoo.otel.models")
    with tracer.start_as_current_span(
        "model.search_read", kind=SpanKind.INTERNAL
    ) as span:
        trace_common(span, self)
        span.set_attribute("odoo.model", self._name)
        span.set_attribute("odoo.domain", str(domain))
        span.set_attribute("odoo.fields", str(fields))  # maybe truncate?
        span.set_attribute("odoo.offset", offset)
        if limit:
            span.set_attribute("odoo.limit", limit)
        if order:
            span.set_attribute("odoo.order", order)
        span.set_attribute("odoo.read_kwargs", str(read_kwargs))  # maybe truncate?

        try:
            res = _model_search_read(
                self,
                domain=domain,
                fields=fields,
                offset=offset,
                limit=limit,
                order=order,
                **read_kwargs,
            )
            span.set_attribute("odoo.result_count", len(res))
            span.set_status(Status(StatusCode.OK))
            return res
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR))
            raise


_model_search_read = models.Model.search_read
_patch_model(models.Model, "search_read", search_read)


def patch_models():
    for model, method_name, method in METHODS_TO_PATCH:
        setattr(model, method_name, method)
