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

from openerp.addons.web import http
from openerp.http import request
from openerp import SUPERUSER_ID


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
        webhook_id = webhook_registry.create(
            cr, SUPERUSER_ID, {}, context=context)
        webhook = webhook_registry.browse(
            cr, SUPERUSER_ID, webhook_id, context=context)
        webhook.run_webhook(request)
