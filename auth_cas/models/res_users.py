# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
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

import logging

import werkzeug.urls
import urlparse
import urllib2
from lxml import etree

import openerp
from openerp import models, fields, api

_logger = logging.getLogger(__name__)


class res_users(models.Model):
    _inherit = 'res.users'

    cas_ticket = fields.Char('Ticket', readonly=True, copy=False)

    @api.model
    def _auth_cas_rpc(self, endpoint, ticket):
        service = self.env['ir.config_parameter'].search(
            [('key', '=', 'auth_cas.url_service')])
        if service:
            service = service[0].value
        else:
            service = self.env['ir.config_parameter'].search(
                [('key', '=', 'web.base.url')])[0].value

        params = werkzeug.url_encode({'ticket': ticket, 'service': service})
        if urlparse.urlparse(endpoint)[4]:
            url = endpoint + '&' + params
        else:
            url = endpoint + '?' + params
        f = urllib2.urlopen(url)
        response = f.read()
        return etree.fromstring(response)

    @api.model
    def _auth_cas_validate(self, ticket):
        """ return the validation data corresponding to the access token """
        p = self.env['ir.config_parameter'].search(
            [('key', '=', 'auth_cas.url_validation')])

        validation = self._auth_cas_rpc(p.value, ticket)

        if validation.xpath("//*[local-name() = 'authenticationFailure']"):
            raise Exception(
                validation.xpath(
                    "//*[local-name() = 'authenticationFailure']")[0].text)

        return validation

    @api.model
    def _auth_cas_signin(self, validation, params):
        """
        Retrieve and sign in the user corresponding to provider and validated
        access token
            :param validation: result of validation of access token (dict)
            :param params: cas parameters (dict)
            :return: user login (str)
            :raise: openerp.exceptions.AccessDenied if signin failed

            This method can be overridden to add alternative signin methods.
        """
        try:
            login = validation.xpath("//*[local-name() = 'user']")[0].text
            user = self.search([("login", "=", login)])
            if not user:
                raise openerp.exceptions.AccessDenied()
            assert len(user) == 1
            user.write({'cas_ticket': params['ticket']})
            return user.login
        except openerp.exceptions.AccessDenied:
            return None

    @api.model
    def auth_cas(self, params):
        ticket = params.get('ticket')
        validation = self._auth_cas_validate(ticket)

        # retrieve and sign in user
        login = self._auth_cas_signin(
            validation, params)
        if not login:
            raise openerp.exceptions.AccessDenied()
        # return user credentials
        return (self.env.cr.dbname, login, ticket)

    @api.model
    def check_credentials(self, password):
        try:
            return super(res_users, self).check_credentials(password)
        except openerp.exceptions.AccessDenied:
            uid = self.env.uid
            res = self.sudo().search(
                [('id', '=', uid), ('cas_ticket', '=', password)])
            if not res:
                raise
