# Copyright (C) 2018 Akretion
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from datetime import timedelta

from odoo import fields, models
from odoo.osv import expression


class IrAttachment(models.Model):
    _name = "ir.attachment"
    _inherit = ["ir.attachment", "autovacuum.mixin"]
    _autovacuum_relation = "assigned_attachment_ids"

    def _get_autovacuum_domain(self, rule):
        domain = super()._get_autovacuum_domain(rule)
        today = fields.Datetime.now()
        limit_date = today - timedelta(days=rule.retention_time)
        create_date_domain = [("create_date", "<", limit_date)]
        domains = [domain, create_date_domain]
        if rule.inheriting_model:
            inheriting_model = self.env[rule.inheriting_model]
            attachment_link = inheriting_model._inherits.get("ir.attachment")
            att_ids = (
                inheriting_model.search(create_date_domain).mapped(attachment_link).ids
            )
            domains.append([("id", "in", att_ids)])
        if rule.filename_pattern:
            domains.append([("name", "ilike", rule.filename_pattern)])
        if rule.model_ids:
            models = rule.model_ids.mapped("model")
            domains.append([("res_model", "in", models)])
        elif not rule.empty_model or not rule.filename_pattern:
            # Avoid deleting attachment without model, if there are, it is
            # probably some attachments created by Odoo
            domains.append([("res_model", "!=", False)])
        return expression.AND(domains)
