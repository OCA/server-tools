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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import urllib
import json

from openerp import models, fields, api


class ResBannedRemote(models.Model):
    _name = 'res.banned.remote'
    _rec_name = 'remote'

    _GEOLOCALISATION_URL = "http://ip-api.com/json/{}"

    # Default Section
    def _default_ban_date(self):
        return fields.Datetime.now()

    # Column Section
    description = fields.Text(
        string='Description', compute='_compute_description', store=True)

    ban_date = fields.Datetime(
        string='Ban Date', required=True, default=_default_ban_date)

    remote = fields.Char(string='Remote ID', required=True)

    active = fields.Boolean(
        string='Active', help="Uncheck this box to unban the remote",
        default=True)

    attempt_ids = fields.Many2many(
        comodel_name='res.authentication.attempt', string='Attempts',
        compute='_compute_attempt_ids')

    # Compute Section
    @api.multi
    @api.depends('remote')
    def _compute_description(self):
        for item in self:
            url = self._GEOLOCALISATION_URL.format(item.remote)
            res = json.loads(urllib.urlopen(url).read())
            item.description = ''
            for k, v in res.iteritems():
                item.description += '%s : %s\n' % (k, v)

    @api.multi
    def _compute_attempt_ids(self):
        for item in self:
            attempt_obj = self.env['res.authentication.attempt']
            item.attempt_ids = attempt_obj.search_last_failed(item.remote).ids
