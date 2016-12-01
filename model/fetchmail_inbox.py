# -*- coding: utf-8 -*-
# © 2014-2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import _, api, models


class FetchmailInbox(models.Model):
    _inherit = 'mail.thread'
    _name = 'fetchmail.inbox'
    _description = 'Fetchmail inbox'

    @api.multi
    def name_get(self):
        mails = self.env['mail.message'].search([
            ('model', '=', self._name),
            ('res_id', 'in', self.ids),
        ])
        return [
            (this.id, mails.filtered(
                lambda x: x.res_id == this.id)[:1].subject or _('Fetchmail inbox'))
            for this in self
        ]
