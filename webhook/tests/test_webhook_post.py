# -*- coding: utf-8 -*-
# Copyright 2016 Vauxoo - https://www.vauxoo.com/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
import requests

from odoo.tests.common import HttpCase
from odoo import api, exceptions, tools, models
from odoo.tools.translate import _


HOST = '127.0.0.1'
PORT = tools.config['http_port']


class Webhook(models.Model):
    _inherit = 'webhook'

    def run_wehook_test_get_foo(self):
        """
        This method is just to test webhook.
        This needs receive a json request with
        next json values: {'foo': 'bar'}
        If value is different will raise a error.
        """
        self.ensure_one()
        if self.env.request.jsonrequest['foo'] != 'bar':
            raise exceptions.ValidationError(_("Wrong value received"))


class FakeHttpRequest(object):
    remote_address = None
    headers = {}


class FakeRequest(object):
    def __init__(self, **args):
        self.httprequest = FakeHttpRequest()


class TestWebhookPost(HttpCase):
    def setUp(self):
        super(TestWebhookPost, self).setUp()
        self.webhook = self.env['webhook']
        self.url_base = "http://%s:%s" % (HOST, PORT)
        self.url = self.get_webhook_url()

    def get_webhook_url(self, url='/webhook',
                        webhook_name="wehook_test"):
        """
        :param string url: Full url of last url of webhook to use.
                    If you use a full url will return url
                    plus session_id
                    default: /webhook
        :param string webhook_name: Name of webhook to process
                    default: webhook_test
        :return: url with
        http://IP:PORT/webhook/webhook_name?session_id=###
        """
        webhook_name = webhook_name.replace('/', '')
        if url.startswith('/'):
            url = self.url_base + url + '/' + webhook_name
        url += '?session_id=' + self.session_id
        return url

    def post_webhook_event(self, event, url, data, remote_ip=None,
                           headers=None, params=None):
        """
        :param string event String: Name of webhook event.
        :param string url: Full url of webhook services.
        :param dict data: Payload data of request.
        :param string remote_ip: Remote IP of webhook to set in
                                 test variable.
        :param dict headers: Request headers with main data.
        :param dict params: Extra values to send to webhook.
        """
        if headers is None:
            headers = {}
        if remote_ip is None:
            remote_ip = '127.0.0.1'
        headers.update({
            'X-Webhook-Test-Event': event,
            'X-Webhook-Test-Address': remote_ip,
        })
        headers.setdefault('accept', 'application/json')
        headers.setdefault('content-type', 'application/json')
        payload = json.dumps(data)
        response = requests.request(
            "POST", url, data=payload,
            headers=headers, params=params)
        return response.json()

    def test_webhook_ping(self):
        """
        Test to check that 'ping' generic method work fine!
        'ping' event don't need to add it in inherit class.
        """
        json_response = self.post_webhook_event(
            'ping', self.url, {})
        has_error = json_response.get('error', False)
        self.assertEqual(
            has_error, False, 'Error in webhook ping test!')

    def test_webhook_get_foo(self):
        """
        Test to check that 'get_foo' event from 'webhook_test'
        work fine!
        This event is defined in inherit method of test.
        """
        json_response = self.post_webhook_event(
            'get_foo', self.url, {'foo': 'bar'})
        self.assertEqual(
            json_response.get('error', False), False,
            'Error in webhook get foo test!.')

    def test_webhook_search_with_request(self):
        """Test to check that 'search_with_request' method works!"""
        fake_req = FakeRequest()
        fake_req.httprequest.headers['X-Webhook-Test-Address'] = '127.0.0.1'
        wh = self.webhook.search_with_request(fake_req)
        self.assertEqual(wh.id, self.env.ref('webhook.webhook_test').id,
                         "Search webhook from request IP info is not working")
