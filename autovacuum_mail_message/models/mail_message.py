# -*- coding: utf-8 -*-
# Copyright (C) 2018 Akretion
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from openerp import api, models
import openerp

import logging
_logger = logging.getLogger(__name__)


class MailMessage(models.Model):
    _inherit = "mail.message"

    @api.multi
    def batch_unlink(self):
        with api.Environment.manage():
            with openerp.registry(
                    self.env.cr.dbname).cursor() as new_cr:
                new_env = api.Environment(new_cr, self.env.uid,
                                          self.env.context)
                self = self.with_env(new_env)
                try:
                    while self:
                        batch_delete_messages = self[0:1000]
                        self -= batch_delete_messages
                        batch_delete_messages.unlink()
                        new_env.cr.commit()
                except Exception as e:
                    _logger.exception(
                        "Failed to delete messages : %s", e)

    @api.model
    def autovacuum_mail_message(self):
        """
            Called by ir.cron
        """
        rules = self.env['message.vacuum.rule'].search([])
        for rule in rules:
            domain = rule.get_message_domain()
            messages = self.search(domain)
            messages.batch_unlink()
