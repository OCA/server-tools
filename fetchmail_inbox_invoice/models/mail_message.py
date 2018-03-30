# coding: utf-8
# Copyright (C) 2014 Therp BV (<http://therp.nl>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class MailMessage(models.Model):
    _inherit = 'mail.message'

    @api.model
    def _needaction_count(self, domain):
        if domain == [('model', '=', 'fetchmail.inbox.invoice')]:
            return len(self.search(domain))
        return super(MailMessage, self)._needaction_count(domain)
