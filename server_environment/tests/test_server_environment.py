# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp (https://www.camptocamp.com).
# License GPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from mock import patch

from odoo.tools.config import config as odoo_config

from .. import server_env
from . import common


class TestEnv(common.ServerEnvironmentCase):

    def test_view(self):
        model = self.env['server.config']
        view = model.fields_view_get()
        self.assertTrue(view)

    def _test_default(self, hidden_pwd=False):
        model = self.env["server.config"]
        rec = model.create({})
        defaults = rec.default_get([])
        self.assertTrue(defaults)
        self.assertIsInstance(defaults, dict)
        pass_checked = False
        for default in defaults:
            if "passw" in default:
                check = self.assertEqual if hidden_pwd else self.assertNotEqual
                check(defaults[default], "**********")
                pass_checked = True
        self.assertTrue(pass_checked)

    @patch.dict(odoo_config.options, {"running_env": "dev"})
    def test_default_dev(self):
        self._test_default()

    @patch.dict(odoo_config.options, {"running_env": "whatever"})
    def test_default_non_dev_env(self):
        self._test_default(hidden_pwd=True)

    @patch.dict(odoo_config.options, {"running_env": "testing"})
    def test_value_retrival(self):
        with self.set_config_dir('testfiles'):
            parser = server_env._load_config()
            val = parser.get('external_service.ftp', 'user')
            self.assertEqual(val, 'testing')
            val = parser.get('external_service.ftp', 'host')
            self.assertEqual(val, 'sftp.example.com')
