from google.cloud import bigquery

from odoo import api, fields, models
from odoo.tools.float_utils import float_repr


class IrModelFieldsBigQuery(models.Model):
    _name = "ir.model.fields.bigquery"
    _description = "Field BigQuery Settings"

    enabled = fields.Boolean(default=True)
    nested = fields.Boolean(
        default=False, help="This will create a struct field in Google BigQuery"
    )
    field_id = fields.Many2one(
        comodel_name="ir.model.fields", ondelete="cascade", required=True
    )
    field_relation = fields.Char(related="parent_id.field_id.relation")
    field_type = fields.Selection(related="field_id.ttype")
    model_bigquery_id = fields.Many2one(
        comodel_name="ir.model.bigquery", string="Model"
    )
    bigquery_type = fields.Selection(
        selection=[
            ("BOOL", "BOOL"),
            ("BYTES", "BYTES"),
            ("DATE", "DATE"),
            ("DATETIME", "DATETIME"),
            ("INTEGER", "INTEGER"),
            ("NUMERIC", "NUMERIC"),
            ("STRING", "STRING"),
            ("STRUCT", "STRUCT"),
        ],
        compute="_compute_bigquery_field_info",
    )
    bigquery_mode = fields.Selection(
        selection=[
            ("NULLABLE", "NULLABLE"),
            ("REQUIRED", "REQUIRED"),
            ("REPEATED", "REPEATED"),
        ],
        compute="_compute_bigquery_field_info",
    )
    parent_id = fields.Many2one(
        comodel_name="ir.model.fields.bigquery",
        ondelete="cascade",
        help="In case of a struct field",
    )
    child_ids = fields.One2many(
        comodel_name="ir.model.fields.bigquery", inverse_name="parent_id"
    )

    # flake8: noqa: C901
    @api.depends("field_type")
    def _compute_bigquery_field_info(self):
        for record in self:
            record.bigquery_mode = record.field_id.required and "REQUIRED" or "NULLABLE"
            if record.field_type == "binary":
                record.bigquery_type = "BYTES"
            elif record.field_type == "boolean":
                record.bigquery_type = "BOOL"
            elif record.field_type == "char":
                record.bigquery_type = "STRING"
            elif record.field_type == "date":
                record.bigquery_type = "DATE"
            elif record.field_type == "datetime":
                record.bigquery_type = "DATETIME"
            elif record.field_type == "float":
                record.bigquery_type = "NUMERIC"
            elif record.field_type == "html":
                record.bigquery_type = "STRING"
            elif record.field_type == "integer":
                record.bigquery_type = "INTEGER"
            elif record.field_type == "many2many":
                record.bigquery_mode = "REPEATED"
                record.bigquery_type = "INTEGER"
                if record.nested:
                    record.bigquery_type = "STRUCT"
            elif record.field_type == "many2one":
                record.bigquery_type = "INTEGER"
                if record.nested:
                    record.bigquery_type = "STRUCT"
            elif record.field_type == "many2one_reference":
                record.bigquery_type = "INTEGER"
            elif record.field_type == "monetary":
                record.bigquery_type = "NUMERIC"
            elif record.field_type == "one2many":
                record.bigquery_mode = "REPEATED"
                record.bigquery_type = "INTEGER"
                if record.nested:
                    record.bigquery_type = "STRUCT"
            elif record.field_type == "reference":
                record.bigquery_type = "STRING"
            elif record.field_type == "selection":
                record.bigquery_type = "STRING"
            elif record.field_type == "text":
                record.bigquery_type = "STRING"

    def to_bigquery_definition(self):
        fields = []
        for record in self:
            field_values = dict(
                name=record.field_id.name,
                field_type=record.bigquery_type,
                mode=record.bigquery_mode,
                description=record.field_id.field_description,
            )
            if record.bigquery_type == "STRUCT":
                child_fields = record.child_ids.to_bigquery_definition()
                field_values["fields"] = child_fields
            fields.append(bigquery.SchemaField(**field_values))
        return fields

    def _convert_value(self, value, record):
        self.ensure_one()
        if self.bigquery_mode == "REPEATED" and self.bigquery_type == "INTEGER":
            return value.ids

        if self.bigquery_mode == "REPEATED" and self.bigquery_type == "STRUCT":
            result = []
            for child in value:
                result.append(self.child_ids.convert_record(child))
            return result

        if self.bigquery_type == "STRUCT":
            return value and self.child_ids.convert_record(value) or None

        if self.bigquery_type == "INTEGER" and self.field_type == "many2one":
            return value and value.id or None

        if self.bigquery_type == "BYTES":
            return value and value.decode() or None

        if self.bigquery_type == "DATETIME":
            return value and fields.Datetime.to_string(value) or None

        if self.bigquery_type == "DATE":
            return value and fields.Date.to_string(value) or None

        if self.bigquery_type == "BOOL":
            return value

        if self.bigquery_type == "NUMERIC":
            field = record._fields[self.field_id.name]
            if self.field_type == "monetary":
                return field.convert_to_column(value, record)
            else:
                digits = field.get_digits(self.env)
                precision = 0
                if type(digits) is int:
                    precision = digits
                elif type(precision) is tuple:
                    precision = digits[1]
                else:
                    precision = 3  # Make it work always even with digits = None
                # float_round doesn't work for values like 234.2000000005, so we use float_repr
                value = float_repr(value, precision_digits=precision)
                return float(value)

        return value or None

    def convert_record(self, record):
        result = {}
        for field in self:
            value = record[field.field_id.name]
            result[field.field_id.name] = field._convert_value(value, record)
        return result

    def toggle_enabled(self):
        for record in self:
            record.enabled = not record.enabled

    def toggle_nested(self):
        for record in self:
            record.nested = not record.nested
