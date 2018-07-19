# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp (https://www.camptocamp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.server_environment import server_env
from .common import ServerEnvironmentCase


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
            val = parser.get('external_service.ftp', 'user')
            self.assertEqual(val, 'foo')
