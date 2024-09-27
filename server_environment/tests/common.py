# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp (https://www.camptocamp.com).
# License GPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os
from contextlib import contextmanager
from mock import patch

from odoo.tests import common
from odoo.addons.server_environment import server_env

import odoo.addons.server_environment.models.server_env_mixin as \
    server_env_mixin


class ServerEnvironmentCase(common.SavepointCase):
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
    def load_config(self, public=None, secret=None, serv_config_class=server_env_mixin):
        original_serv_config = serv_config_class.serv_config
        try:
            with self.set_config_dir(None), \
                    self.set_env_variables(public, secret):
                parser = server_env._load_config()
                serv_config_class.serv_config = parser
                yield

        finally:
            serv_config_class.serv_config = original_serv_config
