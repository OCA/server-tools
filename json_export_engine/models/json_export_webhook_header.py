# Copyright 2026 KOBROS-TECH LTD (https://kobros-tech.com).
# @author Mohamed Alkobrosli <mohamed@kobros-tech.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class JsonExportWebhookHeader(models.Model):
    _name = "json.export.webhook.header"
    _description = "JSON Export Webhook Custom Header"
    _order = "key"

    webhook_id = fields.Many2one(
        "json.export.webhook",
        required=True,
        ondelete="cascade",
    )
    key = fields.Char(string="Header Name", required=True)
    value = fields.Char(string="Header Value", required=True)
