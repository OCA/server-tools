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
from datetime import datetime, timedelta
import urllib
import json
import logging

from openerp import models, fields, api
from openerp.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)


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

    user_id = fields.Many2one(comodel_name='res.users', string='User')

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

    @api.multi
    def write(self, vals):
        # create log entry if the user was unbanned
        if not vals.get('active', True):
            self.on_unban()
        return super(ResBannedRemote, self).write(vals)

    @api.multi
    def unlink(self):
        self.on_unban()
        return super(ResBannedRemote, self).unlink()

    @api.multi
    def on_unban(self):
        for rec in self:
            # avoid log entry if active was already False
            if not rec.active:
                continue
            self.env['res.authentication.attempt'].create({
                'attempt_date': fields.Datetime.now(),
                'login': rec.user_id and rec.user_id.login or False,
                'remote': rec.remote,
                'user_id': rec.user_id and rec.user_id.id or False,
                'result': 'unbanned',
            })

    @api.multi
    def name_get(self):
        result = []

        for rec in self:
            name = rec.remote
            if rec.user_id:
                name = '%s / %s' % (rec.remote, rec.user_id.name_get()[0][1])
            result.append((rec.id, name))

        return result

    @api.model
    def unban_after_ban_time(self):
        attempt_ban_time = self.env['ir.config_parameter'].search_read(
            [('key', '=', 'auth_brute_force.attempt_ban_time')], ['value'])

        # if config parameter doesn't exists: abort
        if not attempt_ban_time:
            return True

        try:
            attempt_ban_time = int(attempt_ban_time[0]['value'])
        except ValueError:
            attempt_ban_time = 0

        # if config parameter is not positive: abort
        if attempt_ban_time <= 0:
            return True

        unban_before = datetime.now() - timedelta(minutes=attempt_ban_time)
        unban_before = unban_before.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        recs = self.search([
            ('active', '=', True),
            ('ban_date', '<', unban_before)])

        if recs:
            recs.write({
                'active': False,
            })

            unbanned_names = map(lambda x: x[1], recs.name_get())
            _logger.info(
                'Unbanned following remotes: %s' % ', '.join(unbanned_names))
