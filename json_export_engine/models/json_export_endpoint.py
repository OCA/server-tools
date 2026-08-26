# Copyright 2026 KOBROS-TECH LTD (https://kobros-tech.com).
# @author Mohamed Alkobrosli <mohamed@kobros-tech.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import re
import secrets

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class JsonExportEndpoint(models.Model):
    _name = "json.export.endpoint"
    _description = "JSON Export REST Endpoint"
    _order = "name"

    name = fields.Char(required=True)
    schema_id = fields.Many2one(
        "json.export.schema",
        string="Export Schema",
        required=True,
        ondelete="cascade",
    )
    active = fields.Boolean(default=True)
    route_path = fields.Char(
        required=True,
        help="URL path segment, e.g. 'products' will map to /api/json_export/products",
    )
    full_url = fields.Char(
        compute="_compute_full_url",
        string="Data URL",
    )
    schema_url = fields.Char(
        compute="_compute_full_url",
        string="Schema URL",
    )
    auth_type = fields.Selection(
        [
            ("none", "No Authentication"),
            ("api_key", "API Key"),
            ("user", "Session (Logged-in User)"),
        ],
        default="api_key",
        required=True,
    )
    api_key = fields.Char(groups="json_export_engine.group_manager")
    api_key_generated_at = fields.Datetime(
        string="API Key Generated At",
        readonly=True,
        groups="json_export_engine.group_manager",
        help="Timestamp of the last API key generation, useful for rotation tracking.",
    )
    paginate = fields.Boolean(
        default=True,
        help="When enabled, results are split into pages. "
        "When disabled, all records are returned in a single response.",
    )
    page_size = fields.Integer(
        default=50,
        help="Number of records per page (used when pagination is enabled).",
    )
    cors_origin = fields.Char(
        string="CORS Origin",
        help="Allowed CORS origin, e.g. * or https://example.com",
    )
    allow_filtering = fields.Boolean(
        default=False,
        help="Allow ?filter[field][op]=value query parameters. "
        "Only fields in the schema parser are filterable.",
    )
    allow_sorting = fields.Boolean(
        default=False,
        help="Allow ?sort=field1,-field2 query parameters. "
        "Only fields in the schema parser are sortable.",
    )
    allow_field_selection = fields.Boolean(
        default=False,
        help="Allow ?fields=field1,field2 to return a subset of fields.",
    )
    rate_limit = fields.Boolean(default=False)
    rate_limit_count = fields.Integer(
        default=60,
        help="Maximum number of requests allowed per rate limit window.",
    )
    rate_limit_window = fields.Integer(
        string="Rate Limit Window (seconds)",
        default=60,
        help="Duration of the sliding window in seconds.",
    )

    @api.onchange("auth_type")
    def _onchange_auth_type(self):
        """Auto-generate an API key when switching to API Key auth."""
        if self.auth_type == "api_key" and not self.api_key:
            self.api_key = secrets.token_hex(32)
            self.api_key_generated_at = fields.Datetime.now()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("auth_type") == "api_key" and not vals.get("api_key"):
                vals["api_key"] = secrets.token_hex(32)
                vals["api_key_generated_at"] = fields.Datetime.now()
        return super().create(vals_list)

    @api.constrains("auth_type", "api_key")
    def _check_api_key_required(self):
        for rec in self:
            if rec.auth_type == "api_key" and not rec.api_key:
                raise ValidationError(
                    _(
                        "An API key is required when authentication"
                        " type is set to 'API Key'. Please generate one."
                    )
                )

    @api.depends("route_path")
    def _compute_full_url(self):
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        for rec in self:
            if rec.route_path:
                path = rec.route_path.strip("/")
                rec.full_url = "%s/api/json_export/%s" % (base_url, path)
                rec.schema_url = "%s/api/json_export/%s/schema" % (base_url, path)
            else:
                rec.full_url = ""
                rec.schema_url = ""

    @api.constrains("route_path")
    def _check_route_path(self):
        for rec in self:
            if not rec.route_path:
                continue
            path = rec.route_path.strip("/")
            if not re.match(r"^[a-zA-Z0-9_/\-]+$", path):
                raise ValidationError(
                    _(
                        "Route path may only contain letters, numbers, "
                        "hyphens, underscores, and slashes."
                    )
                )
            # Check uniqueness among active endpoints
            duplicate = self.search(
                [
                    ("id", "!=", rec.id),
                    ("active", "=", True),
                    ("route_path", "=", path),
                ],
                limit=1,
            )
            if duplicate:
                raise ValidationError(
                    _(
                        "Route path '%(path)s' is already in use"
                        " by endpoint '%(endpoint)s'.",
                        path=path,
                        endpoint=duplicate.name,
                    )
                )

    def action_generate_api_key(self):
        """Generate a new random API key."""
        now = fields.Datetime.now()
        for rec in self:
            rec.api_key = secrets.token_hex(32)
            rec.api_key_generated_at = now
        return True
