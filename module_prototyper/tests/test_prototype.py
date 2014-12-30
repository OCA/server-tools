# -*- encoding: utf-8 -*- #
# OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
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

from jinja2 import Environment
from jinja2.exceptions import TemplateNotFound
from openerp.tests import common


class TestModulePrototyper(common.TransactionCase):
    def setUp(self):
        super(TestModulePrototyper, self).setUp()
        self.main_model = self.env['module_prototyper']
        self.module_category_model = self.env['ir.module.category']
        self.module_module_model = self.env['ir.module.module']

        self.prototype = self.main_model.create({
            'name': 't_name',
            'category_id': self.module_category_model.browse(1).id,
            'human_name': 't_human_name',
            'summary': 't_summary',
            'description': 't_description',
            'author': 't_author',
            'maintainer': 't_maintainer',
            'website': 't_website',
            'dependencies': [(6, 0, [1, 2, 3, 4])],
        })
        self.api_version = '8.0'

    def test_generate_files_assert_if_no_env(self):
        self.assertRaises(
            AssertionError,
            self.prototype.generate_files
        )

    def test_generate_files(self):
        """Test generate_files returns a tuple."""
        self.prototype.set_jinja_env(self.api_version)
        details = self.prototype.generate_files()
        self.assertIsInstance(details, list)
        # namedtuples in tuple
        for file_details in details:
            self.assertIsInstance(file_details, tuple)
            self.assertIsInstance(file_details.filename, basestring)
            self.assertIsInstance(file_details.filecontent, basestring)

    def test_generate_files_raise_templatenotfound_if_not_found(self):
        self.prototype.set_jinja_env('t_api_version')
        self.assertRaises(
            TemplateNotFound,
            self.prototype.generate_files
        )

    def test_set_env(self):
        """test the jinja2 environment is set."""
        self.assertIsNone(self.prototype._env)
        self.prototype.set_jinja_env(self.api_version)
        self.assertIsInstance(
            self.prototype._env, Environment
        )

    def test_friendly_name_return(self):
        """Test if the returns match the pattern."""
        name = 'res.partner'
        self.assertEqual(
            self.prototype.friendly_name(name),
            name.replace('.', '_')
        )
