# -*- encoding: utf-8 -*-
##############################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: moylop260@vauxoo.com
#    planned by: nhomar@vauxoo.com
#                moylop260@vauxoo.com
############################################################################

import pprint

from openerp.addons.web import http
from openerp.http import request
from openerp import SUPERUSER_ID, exceptions
from openerp.tools.translate import _


class WebhookController(http.Controller):

    @http.route('/webhook', type='json', auth='none', method=['POST'])
    def webhook(self, *args, **kwargs):
        '''
        Webhook odoo controller to receive json request and send to
        driver method.
        You will need create your webhook with http://0.0.0.0:0000/webhook
        NOTE: Important use --db-filter params in odoo start.
        '''
        cr, context = request.cr, request.context
        webhook_registry = request.registry['webhook']
        webhook = webhook_registry.search_with_request(
            cr, SUPERUSER_ID, request, context=context)
        if not webhook:
            raise exceptions.ValidationError(_(
                'webhook consumer not found %s' % (
                    pprint.pformat(request.jsonrequest)[:450])))
        webhook.run_webhook(request)
