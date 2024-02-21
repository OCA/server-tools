# Copyright 2024 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class TemplateContentMapping(models.Model):
    _name = "template.content.mapping"
    _description = "Template Content Mapping"
    _order = "template_id, content_from"

    @api.model
    def _lang_get(self):
        return self.env["res.lang"].get_installed()

    name = fields.Char(compute="_compute_name", store=True, readonly=True)
    report_id = fields.Many2one("ir.actions.report")
    template_id = fields.Many2one(
        "ir.ui.view",
        domain=[("type", "=", "qweb")],
        required=True,
        compute="_compute_template_id",
        store=True,
        readonly=False,
        help="Select the main template of the report / frontend page to be modified.",
    )
    lang = fields.Selection(
        _lang_get,
        string="Language",
        default=lambda self: self.env.lang,
        help="If no language is selected, the mapping will be applied to all "
        "languages.",
    )
    active_lang_count = fields.Integer(compute="_compute_active_lang_count")
    content_from = fields.Char(
        required=True,
        help="Set the content (string) to be replaced. e.g. 'Salesperson'.",
    )
    content_to = fields.Char(
        help="Set your new content (string). e.g. 'Sales Representative'.",
    )

    @api.depends("content_from", "content_to")
    def _compute_name(self):
        for record in self:
            record.name = False
            if record.content_from:
                record.name = (
                    f"{record.content_from or ''} -> {record.content_to or ''}"
                )

    @api.depends("report_id")
    def _compute_template_id(self):
        for rec in self:
            rec.template_id = False
            if rec.report_id:
                report_name = rec.report_id.report_name
                rec.template_id = self.env["ir.ui.view"]._get(report_name).sudo()

    @api.depends("lang")
    def _compute_active_lang_count(self):
        lang_count = len(self.env["res.lang"].get_installed())
        for rec in self:
            rec.active_lang_count = lang_count
