# -*- coding: utf-8 -*-
# Copyright 2016 Vauxoo - https://www.vauxoo.com/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import traceback

from odoo import api, exceptions, fields, models, tools
from odoo.tools.safe_eval import safe_eval
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)

try:
    import ipaddress
except ImportError as err:
    _logger.debug(err)


class WebhookAddress(models.Model):
    _name = 'webhook.address'

    name = fields.Char(
        'IP or Network Address',
        required=True,
        help='IP or network address of your consumer webhook:\n'
        'ip address e.g.: 10.10.0.8\n'
        'network address e.g. of: 10.10.0.8/24',
    )
    webhook_id = fields.Many2one(
        'webhook', 'Webhook', required=True, ondelete='cascade')


class Webhook(models.Model):
    _name = 'webhook'

    name = fields.Char(
        'Consumer name',
        required=True,
        help='Name of your consumer webhook. '
             'This name will be used in named of event methods')
    address_ids = fields.One2many(
        'webhook.address', 'webhook_id', 'IP or Network Address',
        required=True,
        help='This address will be filter to know who is '
             'consumer webhook')
    python_code_get_event = fields.Text(
        'Get event',
        required=True,
        help='Python code to get event from request data.\n'
             'You have object.env.request variable with full '
             'webhook request.',
        default='# You can use object.env.request variable '
                'to get full data of webhook request.\n'
                '# Example:\n#request.httprequest.'
                'headers.get("X-Github-Event")',
    )
    python_code_get_ip = fields.Text(
        'Get IP',
        required=True,
        help='Python code to get remote IP address '
             'from request data.\n'
             'You have object.env.request variable with full '
             'webhook request.',
        default='# You can use object.env.request variable '
                'to get full data of webhook request.\n'
                '# Example:\n'
                '#object.env.request.httprequest.remote_addr'
                '\nrequest.httprequest.remote_addr',

    )
    active = fields.Boolean(default=True)

    def process_python_code(self, python_code, request=None):
        """
        Execute a python code with eval.
        :param string python_code: Python code to process
        :param object request: Request object with data of json
                               and http request
        :return: Result of process python code.
        """
        self.ensure_one()
        res = None
        eval_dict = {
            'user': self.env.user,
            'object': self,
            'request': request,
            # copy context to prevent side-effects of eval
            'context': dict(self.env.context),
        }
        try:
            res = safe_eval(python_code, eval_dict)
        except BaseException:
            error = tools.ustr(traceback.format_exc())
            _logger.debug(
                'python_code "%s" with dict [%s] error [%s]',
                python_code, eval_dict, error)
        if isinstance(res, str):
            res = tools.ustr(res)
        return res

    @api.model
    def search_with_request(self, request):
        """
        Method to search of all webhook
        and return only one that match with remote address
        and range of address.
        :param object request: Request object with data of json
                               and http request
        :return: object of webhook found or
                 if not found then return False
        """
        for webhook in self.search([]):
            remote_address = webhook.process_python_code(
                webhook.python_code_get_ip, request)
            if not remote_address:
                continue
            if webhook.is_address_range(remote_address):
                return webhook
        return False

    def is_address_range(self, remote_address):
        """
        Check if a remote IP address is in range of one
        IP or network address of current object data.
        :param string remote_address: Remote IP address
        :return: if remote address match then return True
                 else then return False
        """
        self.ensure_one()
        for address in self.address_ids:
            ipn = ipaddress.ip_network(u'' + address.name)
            hosts = [host.exploded for host in ipn.hosts()]
            hosts.append(address.name)
            if remote_address in hosts:
                return True
        return False

    @api.model
    def get_event_methods(self, event_method_base):
        """
        List all methods of current object that start with base name.
        e.g. if exists methods called 'x1', 'x2'
        and other ones called 'y1', 'y2'
        if you have event_method_base='x'
        Then will return ['x1', 'x2']
        :param string event_method_base: Name of method event base
        returns: List of methods with that start with method base
        """
        # TODO: Filter just callable attributes
        return sorted(
            attr for attr in dir(self) if attr.startswith(
                event_method_base)
        )

    @api.model
    def get_ping_events(self):
        """
        List all name of event type ping.
        This event is a dummy event just to
        know if a provider is working.
        :return: List with names of ping events
        """
        return ['ping']

    def run_webhook(self, request):
        """
        Run methods to process a webhook event.
        Get all methods with base name
        'run_CONSUMER_EVENT*'
        Invoke all methods found.
        :param object request: Request object with data of json
                               and http request
        :return: True
        """
        self.ensure_one()
        event = self.process_python_code(
            self.python_code_get_event, request)
        if not event:
            raise exceptions.ValidationError(_(
                'event is not defined'))
        method_event_name_base = \
            'run_' + self.name + \
            '_' + event
        methods_event_name = self.get_event_methods(method_event_name_base)
        if not methods_event_name:
            # if is a 'ping' event then return True
            # because the request is received fine.
            if event in self.get_ping_events():
                return True
            raise exceptions.ValidationError(_(
                'Not defined methods "%s" yet' % (
                    method_event_name_base)))
        self.env.request = request
        for method_event_name in methods_event_name:
            method = getattr(self, method_event_name)
            res_method = method()
            if isinstance(res_method, list) and len(res_method) == 1:
                if res_method[0] is NotImplemented:
                    _logger.debug(
                        'Not implemented method "%s" yet', method_event_name)
        return True
