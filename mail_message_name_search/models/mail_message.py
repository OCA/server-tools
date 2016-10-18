# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, models
from openerp.osv import expression


class MailMessage(models.Model):

    _inherit = 'mail.message'

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = ['|', '|', ('record_name', operator, name),
                  ('subject', operator, name), ('body', operator, name)]
        if operator in expression.NEGATIVE_TERM_OPERATORS:
            domain = domain[2:]
        rec = self.search(domain + args, limit=limit)
        return rec.name_get()
