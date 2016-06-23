# -*- encoding: utf-8 -*-
##############################################################################
#
#    Tracks Authentication Attempts and Prevents Brute-force Attacks module
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
        ('unbanned', _('Unbanned'))
    ]

    # Column Section
    attempt_date = fields.Datetime(string='Attempt Date')

    login = fields.Char(string='Tried Login')

    remote = fields.Char(string='Remote ID')

    user_id = fields.Many2one(comodel_name='res.users', string='User')

    result = fields.Selection(
        selection=_ATTEMPT_RESULT, string='Authentication Result')

    # Custom Section
    @api.model
    def search_last_failed(self, remote, user_id=False):
        attempt_ban_type = self.env['ir.config_parameter'].search_read(
            [('key', '=', 'auth_brute_force.attempt_ban_type')],
            ['value'])[0]['value']

        domain_check = [('remote', '=', remote)]
        if attempt_ban_type == 'user':
            domain_check = [('user_id', '=', user_id)]

        last_ok = self.search(
            [('result', 'in', ['successfull', 'unbanned'])] + domain_check,
            order='attempt_date desc', limit=1)
        if last_ok:
            return self.search(
                domain_check + [('attempt_date', '>', last_ok.attempt_date)])
        else:
            return self.search(domain_check)
