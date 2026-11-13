# Copyright (C) 2018 Akretion
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from datetime import timedelta

from odoo import fields, models
from odoo.osv import expression


class MailMessage(models.Model):
    _name = "mail.message"
    _inherit = ["mail.message", "autovacuum.mixin"]
    _autovacuum_relation = "message_ids"

    def _get_autovacuum_domain(self, rule):
        domain = super()._get_autovacuum_domain(rule)
        today = fields.Datetime.now()
        limit_date = today - timedelta(days=rule.retention_time)
        domains = [domain, [("date", "<", limit_date)]]
        if rule.message_type != "all":
            domains.append([("message_type", "=", rule.message_type)])
        if rule.model_ids:
            models = rule.model_ids.mapped("model")
            domains.append([("model", "in", models)])
        subtype_ids = rule.message_subtype_ids.ids
        if subtype_ids and rule.empty_subtype:
            domains.append(
                [
                    "|",
                    ("subtype_id", "in", subtype_ids),
                    ("subtype_id", "=", False),
                ]
            )
        elif subtype_ids and not rule.empty_subtype:
            domains.append([("subtype_id", "in", subtype_ids)])
        elif not subtype_ids and not rule.empty_subtype:
            domains.append([("subtype_id", "!=", False)])
        return expression.AND(domains)
