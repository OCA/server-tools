# Copyright (C) 2019 Akretion
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging

import odoo
from odoo import api, models
from odoo.tools.safe_eval import datetime, safe_eval

_logger = logging.getLogger(__name__)


class AutovacuumMixin(models.AbstractModel):
    _name = "autovacuum.mixin"
    _description = "Mixin used to delete messages or attachments"

    def batch_unlink(self):
        with api.Environment.manage():
            with odoo.registry(self.env.cr.dbname).cursor() as new_cr:
                new_env = api.Environment(new_cr, self.env.uid, self.env.context)
                try:
                    while self:
                        batch_delete = self[0:1000]
                        self -= batch_delete
                        # do not attach new env to self because it may be
                        # huge, and the cache is cleaned after each unlink
                        # so we do not want to much record is the env in
                        # which we call unlink because odoo would prefetch
                        # fields, cleared right after.
                        batch_delete.with_env(new_env).unlink()
                        new_env.cr.commit()
                except Exception as e:
                    _logger.exception(
                        "Failed to delete Ms : {} - {}".format(self._name, str(e))
                    )

    # Call by cron
    @api.model
    def autovacuum(self, ttype="message"):
        rules = self.env["vacuum.rule"].search([("ttype", "=", ttype)])
        for rule in rules:
            records = rule._search_autovacuum_records()
            records.batch_unlink()

    def _get_autovacuum_domain(self, rule):
        return []

    def _get_autovacuum_records(self, rule):
        if rule.model_id and rule.model_filter_domain:
            return self._get_autovacuum_records_model(rule)
        return self.search(self._get_autovacuum_domain(rule))

    def _get_autovacuum_records_model(self, rule):
        domain = self._get_autovacuum_domain(rule)
        record_domain = safe_eval(
            rule.model_filter_domain, locals_dict={"datetime": datetime}
        )
        autovacuum_relation = self._autovacuum_relation
        for leaf in domain:
            if not isinstance(leaf, (tuple, list)):
                record_domain.append(leaf)
                continue
            field, operator, value = leaf
            record_domain.append(
                ("{}.{}".format(autovacuum_relation, field), operator, value)
            )
        records = self.env[rule.model_id.model].search(record_domain)
        return self.search(domain + [("res_id", "in", records.ids)])
