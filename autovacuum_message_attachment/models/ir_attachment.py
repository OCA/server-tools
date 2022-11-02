# Copyright (C) 2018 Akretion
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from datetime import datetime, timedelta

from odoo import models


class IrAttachment(models.Model):
    _name = "ir.attachment"
    _inherit = ["ir.attachment", "autovacuum.mixin"]
    _autovacuum_relation = "assigned_attachment_ids"

    def _get_autovacuum_domain(self, rule):
        domain = super()._get_autovacuum_domain(rule)
        today = datetime.now()
        limit_date = today - timedelta(days=rule.retention_time)
        limit_date = datetime.strftime(limit_date, "%Y-%m-%d %H:%M:%S")
        domain += [("create_date", "<", limit_date)]
        if rule.filename_pattern:
            domain += [("name", "ilike", rule.filename_pattern)]
        if rule.model_ids:
            models = rule.model_ids.mapped("model")
            domain += [("res_model", "in", models)]
        else:
            # Avoid deleting attachment without model, if there are, it is
            # probably some attachments created by Odoo
            domain += [("res_model", "!=", False)]
        return domain
