# -*- coding: utf-8 -*-

# Copyright (C) 2019 Akretion
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from openerp import api, models
from openerp.tools.safe_eval import safe_eval
import openerp
import datetime

import logging
_logger = logging.getLogger(__name__)


class AutovacuumMixin(models.AbstractModel):
    _name = "autovacuum.mixin"
    _description = "Mixin used to delete messages or attachments"

    @api.multi
    def batch_unlink(self):
        with api.Environment.manage():
            with openerp.registry(
                    self.env.cr.dbname).cursor() as new_cr:
                new_env = api.Environment(new_cr, self.env.uid,
                                          self.env.context)
                total_records = len(self)
                if total_records:
                    _logger.info("   Deleting %d records from %s"
                                 % (total_records, self._name))
                    try:
                        while self:
                            batch_delete = self[0:1000]
                            batch_delete_size = len(batch_delete)
                            self -= batch_delete
                            # do not attach new env to self because it may be
                            # huge, and the cache is cleaned after each unlink,
                            # so we do not want too much record is the env in
                            # which we call unlink because odoo would prefetch
                            # fields, cleared right after.
                            batch_delete.with_env(new_env).unlink()
                            new_env.cr.commit()
                            _logger.info("   deleted %d records" % batch_delete_size)
                        _logger.info("Deletion complete!")
                    except Exception as e:
                        _logger.exception(
                            "Failed to delete Ms : %s - %s" % (self._name, str(e)))

    # Called by cron
    @api.model
    def autovacuum(self, ttype='message', limit=None):
        rules = self.env['vacuum.rule'].search([('ttype', '=', ttype)])
        for rule in rules:
            _logger.info("Processing autovacuum rule: %s" % rule.name)
            records = rule._search_autovacuum_records(limit=limit)
            records.batch_unlink()

    def _get_autovacuum_domain(self, rule):
        return []

    def _get_autovacuum_records(self, rule, limit=None):
        if rule.model_id and rule.model_filter_domain:
            return self._get_autovacuum_records_model(rule)
        return self.search(self._get_autovacuum_domain(rule), limit=limit)

    def _get_autovacuum_records_model(self, rule):
        domain = self._get_autovacuum_domain(rule)
        record_domain = safe_eval(rule.model_filter_domain,
                                  locals_dict={'datetime': datetime})
        autovacuum_relation = self._autovacuum_relation
        for leaf in domain:
            if not isinstance(leaf, (tuple, list)):
                record_domain.append(leaf)
                continue
            field, operator, value = leaf
            record_domain.append(
                ('%s.%s' % (autovacuum_relation, field), operator, value))
        records = self.env[rule.model_id.model].search(record_domain)
        return self.search(
            domain + [('res_id', 'in', records.ids)]
        )
