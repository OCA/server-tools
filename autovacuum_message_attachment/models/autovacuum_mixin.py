# Copyright (C) 2019 Akretion
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging

import odoo
from odoo import api, models

_logger = logging.getLogger(__name__)


class AutovacuumMixin(models.AbstractModel):
    _name = "autovacuum.mixin"
    _description = "Mixin used to delete messages or attachments"

    @api.multi
    def batch_unlink(self):
        with api.Environment.manage():
            with odoo.registry(
                    self.env.cr.dbname).cursor() as new_cr:
                new_env = api.Environment(new_cr, self.env.uid,
                                          self.env.context)
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
                        "Failed to delete Ms : %s" % (self._name, str(e)))

    # Call by cron
    @api.model
    def autovacuum(self, ttype='message'):
        rules = self.env['vacuum.rule'].search([('ttype', '=', ttype)])
        for rule in rules:
            domain = rule.get_domain()
            records = self.search(domain)
            records.batch_unlink()
