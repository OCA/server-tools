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

import ipaddress

from openerp import api, exceptions, models
from openerp.tools.translate import _


class Webhook(models.TransientModel):
    _name = 'webhook'

    @api.one
    def set_event(self):
        """
        Method to set `self.env.webhook_event` variable
        with name of event of webhook.
        """
        # Not implement yet
        self.env.webhook_event = None

    @api.one
    def set_driver_remote_address(self):
        """
        Method to set `self.env.webhook_driver_address`
        variable with
        self.env.webhook_driver_address['your_webhook_provider']
            = ['ip1', 'ip2']
        or
        self.env.webhook_driver_address['your_webhook_provider']
            = ['ip1/subnet1', 'ip1/subnet2']
        or both cases (ip/subnet or just ip) in same list.

        The name of webhook provider key will use to process events methods
        with next structure: def run_webhook_WEBHOOK-PROVIDER_EVENT(self):
        """
        # Not implement yet
        self.env.webhook_driver_address = {}

    @api.one
    def set_driver_name(self):
        """
        Method to set global variable `self.env.webhook_driver_name`
        executing method self.get_driver_name
        """
        self.set_driver_remote_address()
        # TODO: Why needed [0]
        self.env.webhook_driver_name = self.get_driver_name()[0]

    @api.one
    def set_remote_address(self):
        """
        Method to set global variable `self.env.webhook_remote_address`
        using the variable `remote_addr` from
        `self.env.request.httprequest` global variable.
        """
        self.env.webhook_remote_address = \
            self.env.request.httprequest.remote_addr

    @api.one
    def set_method_event_name(self):
        """
        Method to set global variable `self.env.method_event_name`
        with string value with structure:
        run_webhook_PROVIDER_EVENT
        Where PROVIDER is name of you webhook request.
        Where EVENT is name of event in webhook request.
        This is a method name to auto invoke it with this standard
        """
        self.env.method_event_name = None
        if self.env.webhook_driver_name and self.env.webhook_event:
            self.env.method_event_name = \
                'run_webhook_' + self.env.webhook_driver_name + \
                '_' + self.env.webhook_event

    @api.one
    def set_webhook_env(self, request):
        """
        Method to set global variables in self.env.*
        """
        self.env.request = request
        self.set_remote_address()
        self.set_driver_name()
        self.set_event()
        self.set_method_event_name()

    @api.one
    def get_driver_name(self):
        """
        Method to return `driver_name` using ip address dict
        with key driver name and value ip address.
        from global variable `self.env.webhook_driver_address`.
        Search a match of ip from remote address using
        global variable `self.env.webhook_remote_address`
        """
        for driver_name, address_list in \
                self.env.webhook_driver_address.iteritems():
            if isinstance(address_list, basestring):
                address_list = [address_list]
            for address in address_list:
                ipn = ipaddress.ip_network(u'' + address)
                hosts = [host.exploded for host in ipn.hosts()]
                hosts.append(address)
                if self.env.webhook_remote_address in hosts:
                    return driver_name

    @api.one
    def run_webhook(self, request):
        """
        Method to redirect json request to method to process.
        Using variable global `self.env.method_event_name`
        and execute this method if exists.
        You need add this new methods with inherit.
        """
        self.set_webhook_env(request)
        if self.env.webhook_driver_name is None:
            raise exceptions.ValidationError(_(
                'webhook driver name not found'))
        if self.env.method_event_name is None:
            raise exceptions.ValidationError(_(
                'method event name not found'))
        if not hasattr(self, self.env.method_event_name):
            raise exceptions.ValidationError(_(
                'att "%s" not found' % self.env.method_event_name))
        webhook_method = getattr(self, self.env.method_event_name)
        return webhook_method()
