# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi
#    Copyright 2014 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo.addons.server_environment import server_env
from . import common


class TestEnv(common.ServerEnvironmentCase):

    def test_view(self):
        model = self.env['server.config']
        view = model.fields_view_get()
        self.assertTrue(view)

    def test_default(self):
        model = self.env['server.config']
        rec = model.create({})
        defaults = rec.default_get([])
        self.assertTrue(defaults)
        self.assertIsInstance(defaults, dict)
        pass_checked = False
        for default in defaults:
            if 'passw' in default:
                self.assertNotEqual(defaults[default],
                                    '**********')
                pass_checked = True
        self.assertTrue(pass_checked)

    def test_value_retrival(self):
        with self.set_config_dir('testfiles'):
            parser = server_env._load_config()
            val = parser.get('external_service.ftp', 'user')
            self.assertEqual(val, 'testing')
            val = parser.get('external_service.ftp', 'host')
            self.assertEqual(val, 'sftp.example.com')
