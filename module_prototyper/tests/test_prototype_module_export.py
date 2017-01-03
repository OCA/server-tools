# -*- coding: utf-8 -*-
# #############################################################################
#
# OpenERP, Open Source Management Solution
# This module copyright (C) 2010 - 2014 Savoir-faire Linux
# (<http://www.savoirfairelinux.com>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
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
from odoo.tests import common
import zipfile
import StringIO


class TestPrototypeModuleExport(common.TransactionCase):
    def setUp(self):
        super(TestPrototypeModuleExport, self).setUp()
        self.main_model = self.env['module_prototyper.module.export']
        self.prototype_model = self.env['module_prototyper']
        self.module_category_model = self.env[
            'ir.module.category'
        ]

        self.prototype = self.prototype_model.create({
            'name': 't_name',
            'category_id': self.module_category_model.browse(1).id,
            'human_name': 't_human_name',
            'summary': 't_summary',
            'description': 't_description',
            'author': 't_author',
            'maintainer': 't_maintainer',
            'website': 't_website',
        })

        self.exporter = self.main_model.create({'name': 't_name'})

    def test_action_export_assert_for_wrong_active_model(self):
        """Test if the assertion raises."""
        exporter = self.main_model.with_context(
            active_model='t_active_model'
        ).create({})
        self.assertRaises(
            AssertionError,
            exporter.action_export,
            [exporter.id],
        )

    def test_action_export_update_wizard(self):
        """Test if the wizard is updated during the process."""
        exporter = self.main_model.with_context(
            active_model=self.prototype_model._name,
            active_id=self.prototype.id
        ).create({})
        exporter.action_export(exporter.id)
        self.assertEqual(exporter.state, 'get')
        self.assertEqual(exporter.name, '%s.zip' % (self.prototype.name,))

    def test_zip_files_returns_tuple(self):
        """Test the method return of the method that generate the zip file."""
        ret = self.main_model.zip_files(self.exporter, [self.prototype])
        self.assertIsInstance(ret, tuple)
        self.assertIsInstance(
            ret.zip_file, zipfile.ZipFile
        )

        self.assertIsInstance(
            ret.stringIO, StringIO.StringIO
        )
