# Copyright (C) 2019 Akretion
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging

from odoo import api, models
from odoo.modules.registry import Registry
from odoo.osv import expression
from odoo.tools.safe_eval import datetime, safe_eval

_logger = logging.getLogger(__name__)

# Number of records deleted per unlink() call. Bounds the id list, the SQL
# DELETE size and the per-commit work, independently of how many records the
# rule retrieves (rule.batch_size).
UNLINK_BATCH_SIZE = 5000


class AutovacuumMixin(models.AbstractModel):
    _name = "autovacuum.mixin"
    _description = "Mixin used to delete messages or attachments"

    def batch_unlink(self, batch_size=0):
        # batch_size == -1 => delete everything in a single unlink (no chunking).
        with Registry(self.env.cr.dbname).cursor() as new_cr:
            if batch_size == -1:
                batch_size = len(self)
            if not batch_size or batch_size < new_cr.IN_MAX:
                batch_size = new_cr.IN_MAX
            elif batch_size > new_cr.IN_MAX:
                # Adapt cursor IN_MAX to batch_size if needed:
                # unlink silently chunk using IN_MAX (1000-rows)
                # Assigning on the instance shadows the class attribute
                # for this cursor only, not the class
                # (Cursor.IN_MAX stays 1000)
                new_cr.IN_MAX = batch_size
            new_env = api.Environment(new_cr, self.env.uid, self.env.context)
            try:
                remaining = self
                while remaining:
                    batch_delete = remaining[0:batch_size]
                    remaining -= batch_delete
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
            _logger.info(
                "Autovacuum rule %s: %s %s record(s) matched, deleting...",
                rule.name,
                len(records),
                self._name,
            )
            records.batch_unlink(UNLINK_BATCH_SIZE)

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
            related_model = self.env[rule.model_id.model]
            # Optimizations
            # 1. We have at least 1 mixin-record per related-record
            #    (see _prefix_domain_fields)
            # => we can limit this search and get a free optimization.
            # Reason: len(models) <= len(models mails)

            # 2. The Query is injected directly into the domain as a SQL subquery
            # (res_id IN (SELECT ...)) instead of materialising ids in Python.
            # _search:
            # "No default order is applied when
            #   the method is invoked without parameter ``order``."
            related_query = related_model._search(record_domain, limit=limit)
            mixin_domain = expression.AND(
                [mixin_domain, [("res_id", "in", related_query)]]
            )
        # Use _search (not search): deletion order is irrelevant and _search
        # applies no ORDER BY. The model default (mail.message._order =
        # 'id desc') combined with LIMIT would force Postgres to sort the whole
        # matching set on every batch (~18s for the 15M stock.picking backlog);
        # without it the LIMIT short-circuits the index scan (~70ms).
        return self.browse(self._search(mixin_domain, limit=limit))

    # Retro-compatibility
    _get_autovacuum_records = _get_autovacuum_records_model
