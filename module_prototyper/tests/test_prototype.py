# -*- coding: utf-8 -*-
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

import ast
import lxml.etree

try:
    import pep8
except ImportError:
    pep8 = None

from jinja2 import Environment
from jinja2.exceptions import TemplateNotFound

from odoo.tests import common


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
            'dependency_ids': [(6, 0, [1, 2, 3, 4])],
        })
        self.api_version = self.env['module_prototyper.api_version'].search([
            ('id', '=', self.ref('module_prototyper.api_version_80'))
        ])

    def test_generate_files_assert_if_no_env(self):
        with self.assertRaises(AssertionError):
            self.prototype.generate_files()

    def test_generate_files(self):
        """Test generate_files returns a tuple."""
        self.prototype.setup_env(self.api_version)
        details = self.prototype.generate_files()
        self.assertIsInstance(details, list)
        # namedtuples in tuple
        for file_details in details:
            self.assertIsInstance(file_details, tuple)
            self.assertIsInstance(file_details.filename, basestring)
            self.assertIsInstance(file_details.filecontent, basestring)

            name, contents = file_details
            if name.endswith(".py"):
                # We have a "coding utf-8" line in there, we need to encode
                contents = contents.encode("utf-8")
                ast.parse(contents)
                if pep8:
                    checker = pep8.Checker(
                        name,
                        contents.splitlines(True))
                    res = checker.check_all()
                    self.assertFalse(
                        res,
                        "Python file %s has pep8 errors:\n"
                        "%s\n%s" % (name, checker.report.messages,
                                    repr(contents))
                    )

            elif name.endswith(".xml"):
                # TODO validate valid odoo xml
                lxml.etree.fromstring(contents)

    def test_generate_files_raise_templatenotfound_if_not_found(self):
        not_existing_api = self.env['module_prototyper.api_version'].create({
            'name': 'non_existing_api'
        })
        self.prototype.setup_env(not_existing_api)
        with self.assertRaises(TemplateNotFound):
            self.prototype.generate_files()

    def test_set_env(self):
        """test the jinja2 environment is set."""
        self.assertIsNone(self.prototype._env)
        self.prototype.setup_env(self.api_version)
        self.assertIsInstance(
            self.prototype._env, Environment
        )
        self.assertEqual(
            self.api_version,
            self.prototype._api_version
        )

    def test_friendly_name_return(self):
        """Test if the returns match the pattern."""
        name = 'res.partner'
        self.assertEqual(
            self.prototype.friendly_name(name),
            name.replace('.', '_')
        )
