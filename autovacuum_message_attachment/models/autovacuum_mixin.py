# Copyright (C) 2019 Akretion
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging

from odoo import api, models
from odoo.modules.registry import Registry
from odoo.osv import expression
from odoo.tools.safe_eval import datetime, safe_eval

_logger = logging.getLogger(__name__)


class AutovacuumMixin(models.AbstractModel):
    _name = "autovacuum.mixin"
    _description = "Mixin used to delete messages or attachments"

    def batch_unlink(self):
        with Registry(self.env.cr.dbname).cursor() as new_cr:
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
                _logger.exception(f"Failed to delete Ms : {self._name} - {str(e)}")

    # Call by cron
    @api.model
    def autovacuum(self, ttype="message"):
        rules = self.env["vacuum.rule"].search([("ttype", "=", ttype)])
        for rule in rules:
            records = rule._search_autovacuum_records()
            records.batch_unlink()

    def _get_autovacuum_domain(self, rule):
        return []

    # Domain evaluated on the resource model (rule.model_id) to keep only the
    # records whose linked resource matches the business filter.
    def _get_autovacuum_rule_domain(self, rule):
        if rule.model_id and rule.model_filter_domain:
            return safe_eval(
                rule.model_filter_domain, locals_dict={"datetime": datetime}
            )
        return None

    def _get_autovacuum_limit(self, rule):
        # batch_size caps how many records a single cron run deletes so the
        # whole backlog is not loaded at once; -1 means no limit.
        return rule.batch_size if rule.batch_size > 0 else None

    # Records domain rewritten through the relation so it can run on the
    # resource model instead of on self (message_ids.date -> ...).
    def _prefix_domain_fields(self, prefix, domain):
        if not prefix.endswith("."):
            prefix = f"{prefix}."
        result = []
        for leaf in domain:
            # A string leaf is an operator ('&', '|', '!'): keep it as-is.
            if not isinstance(leaf, tuple | list):
                result.append(leaf)
                continue
            field, operator, value = leaf
            result.append((f"{prefix}{field}", operator, value))
        return result

    def _get_autovacuum_records_model(self, rule):
        limit = self._get_autovacuum_limit(rule)

        # Domain to filter the mixin (e.g. mail.message, mail.attachment)
        mixin_domain = self._get_autovacuum_domain(rule)

        # Domain to filter the model attached to the mixin
        # E.g. SO, PO, ...
        record_domain = self._get_autovacuum_rule_domain(rule)

        # Retrieve only the records impacted
        # Note: for domain "[]", it's pointless to run this test
        if record_domain:
            autovacuum_relation = self._autovacuum_relation
            # Optimization: retrieve the minimum necessary
            # We only want the records with mixin records
            # to be deleted
            record_domain = expression.AND(
                [
                    record_domain,
                    self._prefix_domain_fields(autovacuum_relation, mixin_domain),
                ]
            )
            records = self.env[rule.model_id.model].search(
                record_domain,
                # Thanks to the optimization with _prefix_domain_fields,
                # We now have at least 1 mixin-record per related-record
                # => We can also limit this search here
                #   and this won't affect the final search
                limit=limit,
            )
            mixin_domain = expression.AND(
                [mixin_domain, [("res_id", "in", records.ids)]]
            )
        return self.search(
            mixin_domain,
            limit=limit,
        )

    # Retro-compatibility
    _get_autovacuum_records = _get_autovacuum_records_model
