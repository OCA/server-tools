# Copyright 2026 KOBROS-TECH LTD (https://kobros-tech.com).
# @author Mohamed Alkobrosli <mohamed@kobros-tech.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import copy
import json
import logging
import re
import time

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval

from ..tools.resolver import IrExportsResolver
from ..tools.serializer import JsonExportSerializer

_logger = logging.getLogger(__name__)


class JsonExportSchema(models.Model):
    _name = "json.export.schema"
    _description = "JSON Export Schema"
    _order = "name"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    model_id = fields.Many2one(
        "ir.model",
        string="Model Reference",
        required=True,
        ondelete="cascade",
        domain=[("transient", "=", False)],
    )
    model_name = fields.Char(
        string="Model Name",
        related="model_id.model",
        store=True,
        readonly=True,
        index=True,
    )
    exporter_id = fields.Many2one("ir.exports", string="Field Selector")
    domain = fields.Char(string="Record Filter", default="[]")
    description = fields.Text()
    record_limit = fields.Integer(
        default=100,
        help="Default maximum number of records returned per request.",
    )
    include_record_id = fields.Boolean(
        default=True,
        help="Always include the record ID in exported data.",
    )
    preview_count = fields.Integer(
        default=5, help="Number of records to show in the preview."
    )
    preview_data = fields.Text(compute="_compute_preview_data", string="Preview")
    json_schema = fields.Text(compute="_compute_json_schema", string="JSON Schema")
    endpoint_ids = fields.One2many("json.export.endpoint", "schema_id")
    webhook_ids = fields.One2many("json.export.webhook", "schema_id")
    schedule_ids = fields.One2many("json.export.schedule", "schema_id")
    log_ids = fields.One2many("json.export.log", "schema_id")
    log_count = fields.Integer(compute="_compute_log_count", string="Logs")

    @api.depends("log_ids")
    def _compute_log_count(self):
        for rec in self:
            rec.log_count = len(rec.log_ids)

    @api.depends(
        "model_id", "exporter_id", "domain", "preview_count", "include_record_id"
    )
    def _compute_preview_data(self):
        for rec in self:
            if not rec.model_id or not rec.exporter_id:
                rec.preview_data = ""
                continue
            try:
                records = rec._get_records(limit=rec.preview_count or 5)
                data = rec._serialize_records(records)
                rec.preview_data = json.dumps(data, indent=2, ensure_ascii=False)
            except Exception as e:
                rec.preview_data = json.dumps(
                    {"error": str(e)}, indent=2, ensure_ascii=False
                )

    # -- Operator map for query-param filtering --
    FILTER_OPERATORS = {
        "eq": "=",
        "ne": "!=",
        "like": "like",
        "ilike": "ilike",
        "gt": ">",
        "gte": ">=",
        "lt": "<",
        "lte": "<=",
        "in": "in",
    }
    _FILTER_PARAM_RE = re.compile(
        r"^filter\[([a-zA-Z_][a-zA-Z0-9_]*)\](?:\[([a-z]+)\])?$"
    )

    # -- Odoo field type → JSON Schema type mapping --
    FIELD_TYPE_MAP = {
        "char": {"type": "string"},
        "text": {"type": "string"},
        "html": {"type": "string"},
        "integer": {"type": "integer"},
        "float": {"type": "number"},
        "monetary": {"type": "number"},
        "boolean": {"type": "boolean"},
        "date": {"type": "string", "format": "date"},
        "datetime": {"type": "string", "format": "date-time"},
        "binary": {"type": "string", "contentEncoding": "base64"},
        "selection": {"type": "string"},
        "reference": {"type": "string"},
    }

    @api.depends("model_id", "exporter_id", "include_record_id")
    def _compute_json_schema(self):
        for rec in self:
            if not rec.model_id or not rec.exporter_id:
                rec.json_schema = ""
                continue
            try:
                record_schema = rec._generate_json_schema()
                api_schema = rec._wrap_api_response_schema(record_schema)
                rec.json_schema = json.dumps(api_schema, indent=2, ensure_ascii=False)
            except Exception as e:
                rec.json_schema = json.dumps(
                    {"error": str(e)}, indent=2, ensure_ascii=False
                )

    def _wrap_api_response_schema(self, record_schema, endpoint=None):
        """Wrap a record-level schema in the full API response envelope."""
        nullable_string = {"anyOf": [{"type": "string"}, {"type": "null"}]}
        desc = record_schema.get("description", "")
        description = f"{desc} Supports ?page=N to navigate pages "
        description += "and ?page=last to jump to the last page."
        if endpoint:
            if endpoint.allow_filtering:
                description += (
                    " Supports ?filter[field][op]=value for filtering"
                    " (operators: eq, ne, like, ilike, gt, gte, lt, lte, in)."
                )
            if endpoint.allow_sorting:
                description += (
                    " Supports ?sort=field1,-field2 for sorting"
                    " (prefix with - for descending)."
                )
            if endpoint.allow_field_selection:
                description += (
                    " Supports ?fields=field1,field2 to select" " a subset of fields."
                )
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": f"{record_schema.get('title', 'Export')} — API Response",
            "description": description,
            "type": "object",
            "required": ["success", "data", "pagination", "meta"],
            "additionalProperties": False,
            "properties": {
                "success": {
                    "type": "boolean",
                    "description": "Whether the request was successful.",
                },
                "data": {
                    "type": "array",
                    "description": "List of exported records.",
                    "items": record_schema,
                },
                "pagination": {
                    "type": "object",
                    "description": "Pagination metadata and navigation links.",
                    "required": [
                        "page",
                        "page_size",
                        "total",
                        "pages",
                        "first",
                        "last",
                        "next",
                        "prev",
                    ],
                    "additionalProperties": False,
                    "properties": {
                        "page": {
                            "type": "integer",
                            "description": "Current page number.",
                            "minimum": 1,
                        },
                        "page_size": {
                            "type": "integer",
                            "description": "Number of records per page.",
                            "minimum": 1,
                        },
                        "total": {
                            "type": "integer",
                            "description": "Total number of records "
                            "matching the query.",
                            "minimum": 0,
                        },
                        "pages": {
                            "type": "integer",
                            "description": "Total number of pages.",
                            "minimum": 1,
                        },
                        "first": {
                            "type": "string",
                            "description": "URL to the first page.",
                        },
                        "last": {
                            "type": "string",
                            "description": "URL to the last page.",
                        },
                        "next": {
                            **nullable_string,
                            "description": "URL to the next page, "
                            "or null if on the last page.",
                        },
                        "prev": {
                            **nullable_string,
                            "description": "URL to the previous page, "
                            "or null if on the first page.",
                        },
                    },
                },
                "meta": {
                    "type": "object",
                    "description": "Request metadata.",
                    "required": ["schema", "model", "duration_ms"],
                    "additionalProperties": False,
                    "properties": {
                        "schema": {
                            "type": "string",
                            "description": "Name of the export schema.",
                        },
                        "model": {
                            "type": "string",
                            "description": "Odoo model name.",
                        },
                        "duration_ms": {
                            "type": "integer",
                            "description": "Server-side processing time "
                            "in milliseconds.",
                            "minimum": 0,
                        },
                    },
                },
            },
        }

    def _generate_json_schema(self):
        """Generate a JSON Schema from the resolved parser and model fields."""
        self.ensure_one()
        parser = self._get_parser()
        model = self.env[self.model_name]
        properties, required = self._parser_to_schema_properties(parser, model)
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": self.name,
            "description": f"Auto-generated schema for {self.name} ({self.model_name})",
            "type": "object",
            "properties": properties,
            "required": required,
            "additionalProperties": False,
        }

    def _parser_to_schema_properties(self, parser, model):
        """Convert a jsonify parser list into JSON Schema properties dict.

        :param parser: list like ["id", "name", ("categ_id", ["id", "name"])]
        :param model: Odoo model instance for field introspection
        :return: (properties_dict, required_list)
        """
        properties = {}
        required = []
        for item in parser:
            if isinstance(item, str):
                # Simple field
                field_name = item
                if field_name in model._fields:
                    field_obj = model._fields[field_name]
                    properties[field_name] = self._field_to_schema(field_obj)
                    if field_obj.required:
                        required.append(field_name)
                elif field_name == "id":
                    properties["id"] = {"type": "integer", "description": "Record ID"}
                    required.append("id")
            elif isinstance(item, tuple) and len(item) == 2:
                # Relational field: ("field_name", ["sub_field1", "sub_field2"])
                field_name, sub_fields = item
                if field_name in model._fields:
                    field_obj = model._fields[field_name]
                    properties[field_name] = self._relational_field_to_schema(
                        field_obj, sub_fields
                    )
                    if field_obj.required:
                        required.append(field_name)
        return properties, required

    def _field_to_schema(self, field_obj):
        """Convert a single Odoo field to a JSON Schema property."""
        schema = {}
        field_type = field_obj.type

        if field_type in self.FIELD_TYPE_MAP:
            schema.update(self.FIELD_TYPE_MAP[field_type])
        elif field_type in ("many2one",):
            schema = {"type": "integer", "description": "Related record ID"}
        elif field_type in ("one2many", "many2many"):
            schema = {
                "type": "array",
                "items": {"type": "integer"},
                "description": "List of related record IDs",
            }
        else:
            schema = {"type": "string"}

        # Add field metadata
        if field_obj.string:
            schema["title"] = field_obj.string
        if field_obj.help:
            schema["description"] = field_obj.help

        # Selection choices
        if field_type == "selection" and field_obj.selection:
            try:
                choices = field_obj.selection
                if callable(choices):
                    choices = choices(self.env[field_obj.model_name])
                schema["enum"] = [key for key, _label in choices]
            except Exception:
                _logger.debug(
                    "Could not resolve selection choices for field %s",
                    field_obj.name,
                    exc_info=True,
                )

        # Nullable for non-required fields
        if not field_obj.required:
            schema = {"anyOf": [schema, {"type": "null"}]}

        return schema

    def _relational_field_to_schema(self, field_obj, sub_fields):
        """Convert a relational field with sub-fields to a JSON Schema property."""
        comodel_name = field_obj.comodel_name
        if comodel_name not in self.env:
            return {"type": "string"}

        comodel = self.env[comodel_name]
        sub_properties, sub_required = self._parser_to_schema_properties(
            sub_fields, comodel
        )

        item_schema = {
            "type": "object",
            "properties": sub_properties,
            "additionalProperties": False,
        }
        if sub_required:
            item_schema["required"] = sub_required

        if field_obj.type == "many2one":
            # Many2one returns a single object (or null)
            schema = {
                "anyOf": [item_schema, {"type": "null"}],
                "title": field_obj.string or field_obj.name,
            }
        else:
            # One2many / Many2many returns an array
            schema = {
                "type": "array",
                "items": item_schema,
                "title": field_obj.string or field_obj.name,
            }
        return schema

    def _get_parser(self):
        """Resolve the ir.exports field selection into a jsonify-compatible parser."""
        self.ensure_one()
        if not self.exporter_id:
            raise UserError(_("Please select a field selector (exporter) first."))
        # Remove broken export lines (e.g. name=False) before parsing,
        # otherwise jsonifier's get_json_parser() crashes on .split("/")
        bad_lines = self.exporter_id.export_fields.filtered(
            lambda field: not field.name
        )
        if bad_lines:
            bad_lines.unlink()
        raw_parser = self.exporter_id.get_json_parser()
        resolved = IrExportsResolver(raw_parser).resolved_parser
        if self.include_record_id and "id" not in resolved:
            resolved.insert(0, "id")
        return resolved

    def _get_serializer(self):
        """Return a configured JsonExportSerializer."""
        self.ensure_one()
        parser = self._get_parser()
        return JsonExportSerializer(parser)

    def _get_domain(self):
        """Parse the domain filter string."""
        self.ensure_one()
        try:
            return safe_eval(self.domain or "[]")
        except Exception:
            return []

    def _get_records(
        self, limit=None, offset=0, extra_domain=None, no_limit=False, order=None
    ):
        """Search for records matching the schema's domain.

        :param limit: Max records to return. None means use schema default.
        :param no_limit: If True, ignore limit and return all matching records.
        :param order: Optional Odoo order string, e.g. "name asc, id desc".
        """
        self.ensure_one()
        domain = self._get_domain()
        if extra_domain:
            domain += extra_domain
        model = self.env[self.model_name]
        search_limit = None if no_limit else (limit or self.record_limit or 100)
        return model.search(domain, limit=search_limit, offset=offset, order=order)

    def _serialize_records(self, records):
        """Serialize a recordset using this schema's configuration."""
        self.ensure_one()
        serializer = self._get_serializer()
        return serializer.serialize_many(records)

    def _serialize_records_with_parser(self, records, parser):
        """Serialize a recordset using an explicit parser (for field selection)."""
        self.ensure_one()
        serializer = JsonExportSerializer(parser)
        return serializer.serialize_many(records)

    # -- Query parameter helpers --

    def _get_allowed_query_fields(self):
        """Return the set of top-level field names from the parser.

        This is the security boundary for filtering, sorting, and field selection.
        """
        self.ensure_one()
        parser = self._get_parser()
        result = set()
        for item in parser:
            if isinstance(item, str):
                result.add(item)
            elif isinstance(item, tuple) and len(item) == 2:
                result.add(item[0])
        return result

    def _build_filter_domain(self, params, allowed_fields):
        """Parse filter[field][op]=value from werkzeug MultiDict into Odoo domain.

        :param params: werkzeug ImmutableMultiDict (request.args)
        :param allowed_fields: set of allowed field names
        :return: list of Odoo domain tuples
        :raises ValueError: on invalid field, operator, or value
        """
        self.ensure_one()
        domain = []
        for key in params:
            match = self._FILTER_PARAM_RE.match(key)
            if not match:
                continue
            field_name = match.group(1)
            operator = match.group(2) or "eq"
            raw_value = params[key]

            if field_name not in allowed_fields:
                raise ValueError(f"Filtering on field '{field_name}' is not allowed.")
            if operator not in self.FILTER_OPERATORS:
                raise ValueError(f"Unknown filter operator '{operator}'.")

            odoo_op = self.FILTER_OPERATORS[operator]
            value = self._coerce_filter_value(field_name, operator, raw_value)
            domain.append((field_name, odoo_op, value))
        return domain

    def _coerce_filter_value(self, field_name, operator, raw_value):
        """Convert a string query-param value to the correct Python type.

        :param field_name: Odoo field name
        :param operator: filter operator key (eq, in, etc.)
        :param raw_value: raw string from query param
        :return: coerced value
        :raises ValueError: on type conversion failure
        """
        self.ensure_one()
        model = self.env[self.model_name]
        field_obj = model._fields.get(field_name)
        field_type = field_obj.type if field_obj else "char"

        if operator == "in":
            parts = [p.strip() for p in raw_value.split(",") if p.strip()]
            return [self._coerce_single_value(field_type, p) for p in parts]

        return self._coerce_single_value(field_type, raw_value)

    @staticmethod
    def _coerce_single_value(field_type, raw):
        """Coerce a single string value based on Odoo field type."""
        if field_type in ("integer", "many2one"):
            try:
                return int(raw)
            except (ValueError, TypeError) as err:
                raise ValueError(f"Expected integer value, got '{raw}'.") from err
        elif field_type in ("float", "monetary"):
            try:
                return float(raw)
            except (ValueError, TypeError) as err:
                raise ValueError(f"Expected numeric value, got '{raw}'.") from err
        elif field_type == "boolean":
            if raw.lower() in ("true", "1", "yes"):
                return True
            elif raw.lower() in ("false", "0", "no"):
                return False
            raise ValueError(f"Expected boolean value, got '{raw}'.")
        return raw

    def _build_sort_order(self, sort_param, allowed_fields):
        """Parse sort=field1,-field2 into Odoo order string.

        :param sort_param: raw sort query param string
        :param allowed_fields: set of allowed field names
        :return: Odoo order string, e.g. "name asc, create_date desc"
        :raises ValueError: on invalid field name
        """
        parts = []
        for token in sort_param.split(","):
            token = token.strip()
            if not token:
                continue
            if token.startswith("-"):
                field_name = token[1:]
                direction = "desc"
            else:
                field_name = token
                direction = "asc"
            if field_name not in allowed_fields:
                raise ValueError(f"Sorting on field '{field_name}' is not allowed.")
            parts.append(f"{field_name} {direction}")
        return ", ".join(parts)

    def _filter_parser(self, fields_param):
        """Filter the schema parser to include only the requested fields.

        :param fields_param: comma-separated field names string
        :return: filtered parser list
        :raises ValueError: on invalid field name
        """
        self.ensure_one()
        requested = {f.strip() for f in fields_param.split(",") if f.strip()}
        allowed = self._get_allowed_query_fields()
        invalid = requested - allowed
        if invalid:
            raise ValueError(
                f"Field selection on '{', '.join(sorted(invalid))}' is not allowed."
            )
        full_parser = self._get_parser()
        filtered = []
        for item in full_parser:
            if isinstance(item, str) and item in requested:
                filtered.append(item)
            elif isinstance(item, tuple) and len(item) == 2 and item[0] in requested:
                filtered.append(copy.deepcopy(item))
        return filtered

    def action_preview(self):
        """Refresh the preview data."""
        self.ensure_one()
        self._compute_preview_data()
        return True

    def action_export_json(self):
        """Manual export: serialize all matching records and create an attachment."""
        self.ensure_one()
        start_time = time.time()
        try:
            records = self._get_records()
            data = self._serialize_records(records)
            content = json.dumps(data, indent=2, ensure_ascii=False)
            filename = (
                f"export_{self.model_name.replace('.', '_')}_"
                f"{fields.Datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            attachment = self.env["ir.attachment"].create(
                {
                    "name": filename,
                    "type": "binary",
                    "datas": base64.b64encode(content.encode("utf-8")),
                    "mimetype": "application/json",
                    "res_model": self._name,
                    "res_id": self.id,
                }
            )
            duration = int((time.time() - start_time) * 1000)
            self._create_log("manual", "success", len(records), duration)
            return {
                "type": "ir.actions.act_url",
                "url": f"/web/content/{attachment.id}?download=true",
                "target": "new",
            }
        except Exception as e:
            duration = int((time.time() - start_time) * 1000)
            self._create_log("manual", "error", 0, duration, error_message=str(e))
            raise UserError(_("Export failed: %s") % str(e)) from e

    def action_view_logs(self):
        """Open log entries for this schema."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Export Logs"),
            "res_model": "json.export.log",
            "view_mode": "list,form",
            "domain": [("schema_id", "=", self.id)],
            "context": {"default_schema_id": self.id},
        }

    def _create_log(
        self,
        log_type,
        status,
        records_count=0,
        duration_ms=0,
        error_message=None,
        request_info=None,
    ):
        """Helper to create a log entry."""
        self.ensure_one()
        return (
            self.env["json.export.log"]
            .sudo()
            .create(
                {
                    "schema_id": self.id,
                    "log_type": log_type,
                    "status": status,
                    "records_count": records_count,
                    "duration_ms": duration_ms,
                    "error_message": error_message,
                    "request_info": request_info,
                }
            )
        )

    def _register_hook(self):
        """Register webhook triggers on target models."""
        res = super()._register_hook()
        schemas = self.sudo().search(
            [
                ("active", "=", True),
                ("webhook_ids.active", "=", True),
            ]
        )
        for schema in schemas:
            schema._patch_model_for_webhooks()
        return res

    def _patch_model_for_webhooks(self):
        """Dynamically patch the target model to fire webhooks on CUD operations."""
        self.ensure_one()
        model_name = self.model_name
        if not model_name or model_name not in self.env:
            return

        model_cls = type(self.env[model_name])
        patch_attr = "_json_export_webhook_patched"

        if getattr(model_cls, patch_attr, False):
            return

        original_create = model_cls.create
        original_write = model_cls.write
        original_unlink = model_cls.unlink

        @api.model_create_multi
        def patched_create(self_model, vals_list):
            records = original_create(self_model, vals_list)
            if not self_model.env.context.get("json_export_skip_webhook"):
                self_model.env["json.export.webhook"].sudo()._fire_for_model(
                    self_model._name, "create", records
                )
            return records

        def patched_write(self_model, vals):
            res = original_write(self_model, vals)
            if not self_model.env.context.get("json_export_skip_webhook"):
                self_model.env["json.export.webhook"].sudo()._fire_for_model(
                    self_model._name, "write", self_model
                )
            return res

        def patched_unlink(self_model):
            # Capture data before deletion
            if not self_model.env.context.get("json_export_skip_webhook"):
                self_model.env["json.export.webhook"].sudo()._fire_for_model(
                    self_model._name, "unlink", self_model
                )
            return original_unlink(self_model)

        model_cls.create = patched_create
        model_cls.write = patched_write
        model_cls.unlink = patched_unlink
        setattr(model_cls, patch_attr, True)
