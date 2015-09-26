# -*- encoding: utf-8 -*-
##############################################################################
#
#    Authentification - Track And Prevent Brut Force module for Odoo
#    Copyright (C) 2015-Today GRAP (http://www.grap.coop)
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api
from openerp.tools.translate import _


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
