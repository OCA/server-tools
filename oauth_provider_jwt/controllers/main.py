# -*- coding: utf-8 -*-
# Copyright 2016 SYLEAM
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import werkzeug
from openerp import http
from openerp.addons import oauth_provider
from openerp.addons.web.controllers.main import ensure_db


class OAuth2ProviderController(
        oauth_provider.controllers.main.OAuth2ProviderController):
    @http.route(
        '/oauth2/public_key', type='http', auth='none', methods=['GET'])
    def public_key(self, client_id=None, *args, **kwargs):
        """ Returns the public key of the requested client """
        ensure_db()

        client = http.request.env['oauth.provider.client'].sudo().search([
            ('identifier', '=', client_id),
        ])
        return werkzeug.wrappers.BaseResponse(
            client.jwt_public_key or '', status=200)
