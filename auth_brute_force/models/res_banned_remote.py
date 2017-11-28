# Copyright 2015 GRAP - Sylvain LE GAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import urllib.request, urllib.parse, urllib.error
import json

from odoo import api, fields, models


class ResBannedRemote(models.Model):
    _name = 'res.banned.remote'
    _rec_name = 'remote'

    _GEOLOCALISATION_URL = "http://ip-api.com/json/{}"

    # Column Section
    description = fields.Text(
        string='Description', compute='_compute_description', store=True)
    ban_date = fields.Datetime(
        string='Ban Date', required=True, default=fields.Datetime.now)
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
            res = json.loads(urllib.request.urlopen(url).read())
            item.description = ''
            for k, v in res.items():
                item.description += '%s : %s\n' % (k, v)

    @api.multi
    def _compute_attempt_ids(self):
        for item in self:
            attempt_obj = self.env['res.authentication.attempt']
            item.attempt_ids = attempt_obj.search_last_failed(item.remote)
