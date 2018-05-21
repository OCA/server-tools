# Copyright 2015 GRAP - Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models


class ResAuthenticationAttempt(models.Model):
    _name = 'res.authentication.attempt'
    _order = 'attempt_date desc'

    _ATTEMPT_RESULT = [
        ('successfull', _('Successfull')),
        ('failed', _('Failed')),
        ('banned', _('Banned')),
    ]

    # Column Section
    attempt_date = fields.Datetime(string='Attempt Date')
    login = fields.Char(string='Tried Login')
    remote = fields.Char(string='Remote ID')
    result = fields.Selection(
        selection=_ATTEMPT_RESULT, string='Authentication Result')

    # Custom Section
    @api.model
    def search_last_failed(self, remote):
        last_ok = self.search(
            [('result', '=', 'successfull'), ('remote', '=', remote)],
            order='attempt_date desc', limit=1)
        if last_ok:
            return self.search([
                ('remote', '=', remote),
                ('attempt_date', '>', last_ok.attempt_date)])
        else:
            return self.search([('remote', '=', remote)])
