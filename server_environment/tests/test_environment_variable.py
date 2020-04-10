# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp (https://www.camptocamp.com).
# License GPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from mock import patch

from odoo.tools.config import config as odoo_config

from odoo.addons.server_environment import server_env
from .common import ServerEnvironmentCase


class TestRunningEnvDefault(ServerEnvironmentCase):
    def test_running_env_default(self):
        """When var is not provided it defaults to `test`."""
        self.assertEqual(odoo_config["running_env"], "test")


@patch.dict(odoo_config.options, {"running_env": "testing"})
class TestEnvironmentVariables(ServerEnvironmentCase):

    def test_env_variables(self):
        public = (
            "[section]\n"
            "foo=bar\n"
            "bar=baz\n"
        )
        secret = (
            "[section]\n"
            "bar=foo\n"
            "alice=bob\n"
        )
        with self.set_config_dir(None), \
                self.set_env_variables(public, secret):
            parser = server_env._load_config()
            self.assertEqual(
                list(parser.sections()),
                ['section']
            )
            self.assertDictEqual(
                dict(parser.items('section')),
                {'alice': 'bob',
                 'bar': 'foo',
                 'foo': 'bar'}
            )

    def test_env_variables_override(self):
        public = (
            "[external_service.ftp]\n"
            "user=foo\n"
        )
        with self.set_config_dir('testfiles'), \
                self.set_env_variables(public):
            parser = server_env._load_config()
            val = parser.get("external_service.ftp", "user")
            self.assertEqual(val, "foo")
