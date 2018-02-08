# -*- coding: utf-8 -*-
# Copyright 2018 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests import SingleTransactionCase
from ..models.letsencrypt import _get_data_dir, WILDCARD
from os import path
import shutil
import mock
import os


class TestLetsencrypt(SingleTransactionCase):

    post_install = True
    at_install = False

    def setUp(self):
        super(TestLetsencrypt, self).setUp()

    def test_config_settings(self):
        settings_model = self.env['base.config.settings']
        letsencrypt_model = self.env['letsencrypt']
        settings = settings_model.create({
            'dns_provider': 'shell',
            'script': 'touch /tmp/.letsencrypt_test',
            'altnames':
                'test.example.com',
            'reload_command': 'echo',
            })
        self.env['ir.config_parameter'].set_param(
            'web.base.url', 'http://www.example.com')
        settings.set_dns_provider()
        setting_vals = settings.default_get([])
        self.assertEquals(setting_vals['dns_provider'], 'shell')
        letsencrypt_model._call_cmdline(setting_vals['script'], shell=True)
        self.assertEquals(path.exists('/tmp/.letsencrypt_test'), True)
        self.assertEquals(
            setting_vals['altnames'],
            settings.altnames,
        )
        self.assertEquals(setting_vals['reload_command'], 'echo')
        settings.onchange_altnames()
        self.assertEquals(settings.needs_dns_provider, False)
        settings.unlink()

    def new_order(self, typ):
        if typ not in ['http-01', 'dns-01']:
            raise ValueError
        authzr = mock.Mock
        order_resource = mock.Mock
        order_resource.fullchain_pem = 'test'
        authorization = mock.Mock
        body = mock.Mock
        challenge = mock.Mock
        challenge.chall = mock.Mock
        challenge.chall.typ = typ
        challenge.chall.token = 'a_token'
        body.challenges = [challenge]
        authorization.body = body
        authzr.authorizations = [authorization]
        return authzr

    def poll(self, deadline):
        order_resource = mock.Mock
        order_resource.fullchain_pem = 'chain'
        return order_resource

    @mock.patch('acme.client.ClientV2.answer_challenge')
    @mock.patch('acme.client.ClientV2.poll_and_finalize', side_effect=poll)
    def test_http_challenge(self, poll, answer_challenge):
        letsencrypt = self.env['letsencrypt']
        self.env['ir.config_parameter'].set_param(
            'web.base.url', 'http://www.example.com')
        settings = self.env['base.config.settings']
        settings.create({
            'altnames': 'test.example.com',
            }).set_dns_provider()
        letsencrypt._cron()
        poll.assert_called()
        self.assertTrue(
            open(path.join(_get_data_dir(), 'www.example.com.crt')).read(),
        )
        os.remove(path.join(_get_data_dir(), 'www.example.com.crt'))

    @mock.patch('acme.client.ClientV2.answer_challenge')
    @mock.patch('acme.client.ClientV2.poll_and_finalize', side_effect=poll)
    def test_dns_challenge(self, poll, answer_challenge):
        letsencrypt = self.env['letsencrypt']
        settings = self.env['base.config.settings']
        settings.create({
            'dns_provider': 'shell',
            'script': 'echo',
            'altnames': WILDCARD + 'example.com',
        }).set_dns_provider()
        letsencrypt._cron()
        poll.assert_called()
        self.assertTrue(
            open(path.join(_get_data_dir(), 'www.example.com.crt')).read(),
        )

    def tearDown(self):
        super(TestLetsencrypt, self).tearDown()
        shutil.rmtree(_get_data_dir(), ignore_errors=True)
