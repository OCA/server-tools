# -*- coding: utf-8 -*-
# Copyright 2016 Vauxoo - https://www.vauxoo.com/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import pprint

from odoo import http
from odoo.http import request
from odoo import exceptions
from odoo.tools.translate import _


class WebhookController(http.Controller):

    @http.route(['/webhook/<webhook_name>'], type='json',
                auth='none', method=['POST'])
    def webhook(self, webhook_name, **post):
        '''
        :params string webhook_name: Name of webhook to use
        Webhook odoo controller to receive json request and send to
        driver method.
        You will need create your webhook with http://0.0.0.0:0000/webhook
        NOTE: Important use --db-filter params in odoo start.
        '''
        # Deprecated by webhook_name dynamic name
        # webhook = webhook_registry.search_with_request(
        #     cr, SUPERUSER_ID, request, context=context)
        webhook = request.env['webhook'].sudo().search(
            [('name', '=', webhook_name)], limit=1)
        # TODO: Add security by secret string  or/and ip consumer
        if not webhook:
            remote_addr = getattr(request.httprequest, 'remote_addr', None)
            raise exceptions.ValidationError(_(
                'webhook consumer [%s] from remote address [%s] '
                'not found jsonrequest [%s]' % (
                    webhook_name,
                    remote_addr,
                    pprint.pformat(request.jsonrequest)[:450]
                )))
        webhook.run_webhook(request)
