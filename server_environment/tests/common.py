# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp (https://www.camptocamp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os
from contextlib import contextmanager
from mock import patch

from odoo.tests import common
from odoo.addons.server_environment import server_env
from odoo.tools.config import config

import odoo.addons.server_environment.models.server_env_mixin as \
    server_env_mixin


class ServerEnvironmentCase(common.SavepointCase):

    def setUp(self):
        super(ServerEnvironmentCase, self).setUp()
        self._original_running_env = config.get('running_env')
        config['running_env'] = 'testing'

    def tearDown(self):
        super(ServerEnvironmentCase, self).tearDown()
        config['running_env'] = self._original_running_env

    @contextmanager
    def set_config_dir(self, path):
        original_dir = server_env._dir
        if path and not os.path.isabs(path):
            path = os.path.join(os.path.dirname(__file__,), path)
        server_env._dir = path
        try:
            yield
        finally:
            server_env._dir = original_dir

    @contextmanager
    def set_env_variables(self, public=None, secret=None):
        newkeys = {}
        if public:
            newkeys['SERVER_ENV_CONFIG'] = public
        if secret:
            newkeys['SERVER_ENV_CONFIG_SECRET'] = secret
        with patch.dict('os.environ', newkeys):
            yield

    @contextmanager
    def load_config(self, public=None, secret=None):
        original_serv_config = server_env_mixin.serv_config
        try:
            with self.set_config_dir(None), \
                    self.set_env_variables(public, secret):
                parser = server_env._load_config()
                server_env_mixin.serv_config = parser
                yield

        finally:
            server_env_mixin.serv_config = original_serv_config
