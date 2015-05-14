# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Business Applications
#    Copyright (c) 2014 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#                       Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
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

from openerp import models, fields, api, exceptions, _
try:
    from txlib.http.auth import BasicAuth
    from txlib.http.http_requests import HttpRequest
    from txlib.http.exceptions import AuthorizationError
except ImportError:
    BasicAuth = HttpRequest = AuthorizationError = None
from requests.exceptions import ConnectionError
try:
    from github import Github
except ImportError:
    Github = None


class TransbotConfigSettings(models.TransientModel):
    _name = 'transbot.config.settings'
    _inherit = 'res.config.settings'

    transifex_url = fields.Char(string="Transifex base URL")
    transifex_user = fields.Char(string="Transifex user")
    transifex_password = fields.Char(string="Transifex password")
    transifex_organization = fields.Char(
        string="Transifex organization",
        help="This is the slug of the Transifex organization to be used for "
             "the creation of new projects, and for the checking of new "
             "translations made")
    transifex_team = fields.Integer(
        string="Transifex team number",
        help="This is the number of the team responsible for making the "
             "transbot translations")
    github_token = fields.Char(string="Github token")

    def get_github_connection(self):
        rec = self._get_parameter('github.token')
        if not rec:
            raise exceptions.Warning(_('There is no Github token defined'))
        else:
            return Github(login_or_token=rec.value)

    def get_transifex_connection(self):
        transifex_url = self._get_parameter('transifex.url').value
        transifex_user = self._get_parameter('transifex.user').value
        transifex_password = self._get_parameter('transifex.password').value
        if not transifex_url or not transifex_user or not transifex_password:
            raise exceptions.Warning(_('Transifex credentials are not fully '
                                       'defined'))
        else:
            auth = BasicAuth(transifex_user, transifex_password)
            return HttpRequest(transifex_url, auth=auth)

    def _get_parameter(self, key):
        param_obj = self.env['ir.config_parameter']
        rec = param_obj.search([('key', '=', key)])
        return rec or False

    @api.multi
    def get_default_parameters(self):
        res = {}
        rec = self._get_parameter('transifex.url')
        res['transifex_url'] = rec and rec.value or 'www.transifex.com'
        rec = self._get_parameter('transifex.user')
        res['transifex_user'] = rec and rec.value or ''
        rec = self._get_parameter('transifex.password')
        res['transifex_password'] = rec and rec.value or ''
        rec = self._get_parameter('transifex.organization')
        res['transifex_organization'] = rec and rec.value or ''
        rec = self._get_parameter('transifex.team')
        res['transifex_team'] = rec and int(rec.value) or ''
        rec = self._get_parameter('github.token')
        res['github_token'] = rec and rec.value or ''
        return res

    def _write_or_create_param(self, key, value):
        if not value:
            return
        param_obj = self.env['ir.config_parameter']
        rec = self._get_parameter(key)
        if rec:
            rec.value = value
        else:
            param_obj.create({'key': key, 'value': value})

    @api.multi
    def set_parameters(self):
        self._write_or_create_param('transifex.url', self.transifex_url)
        self._write_or_create_param('transifex.user', self.transifex_user)
        self._write_or_create_param('transifex.password',
                                    self.transifex_password)
        self._write_or_create_param('transifex.organization',
                                    self.transifex_organization)
        self._write_or_create_param('transifex.team',
                                    str(self.transifex_team))
        self._write_or_create_param('github.token',
                                    self.github_token)

    @api.multi
    def check_transifex(self):
        h = self.get_transifex_connection()
        example_path = '/api/2/language/en'
        try:
            h.get(example_path)
            raise exceptions.Warning("Successful connection")
        except ConnectionError:
            raise exceptions.Warning("Couldn't set connection")
        except AuthorizationError:
            raise exceptions.Warning("Incorrect credentials")
