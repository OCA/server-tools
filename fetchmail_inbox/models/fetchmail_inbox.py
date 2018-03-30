# -*- coding: utf-8 -*-
# © 2014-2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, api, models


class FetchmailInbox(models.Model):
    _inherit = 'mail.thread'
    _name = 'fetchmail.inbox'
    _description = 'Fetchmail inbox'

    @api.multi
    def name_get(self):
        return ([
            (inbox.id, inbox.message_ids[:1].subject or _('Fetchmail inbox'))
            for inbox in self])
