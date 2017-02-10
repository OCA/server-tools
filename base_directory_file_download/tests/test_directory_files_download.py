# -*- coding: utf-8 -*-
# Copyright 2017-2018 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import os
from tempfile import gettempdir

from odoo.tests import common
from odoo.exceptions import UserError


class TestBaseDirectoryFilesDownload(common.TransactionCase):

    def test_01_create(self):
        test_dir = self.env['ir.filesystem.directory'].create({
            'name': 'Test Directory 1',
            'directory': gettempdir()
        })

        # test method get_dir()
        full_dir = test_dir.get_dir()
        self.assertEqual(full_dir[-1], '/')

        # test computed field file_ids
        self.assertGreaterEqual(len(test_dir.file_ids), 0)

        # test count list of directory
        self.assertEqual(len(test_dir.file_ids), test_dir.file_count)

        # test reload list of directory
        test_dir.reload()
        self.assertEqual(len(test_dir.file_ids), test_dir.file_count)

        # test content of files
        for file in test_dir.file_ids:
            filename = file.stored_filename
            directory = test_dir.get_dir()
            with open(os.path.join(directory, filename), 'rb') as f:
                content = f.read().encode('base64')
                self.assertEqual(file.file_content, content)

        # test onchange directory (to not existing)
        test_dir.directory = '/txxx'
        with self.assertRaises(UserError):
            test_dir.onchange_directory()
        self.assertEqual(len(test_dir.file_ids), 0)
        with self.assertRaises(UserError):
            test_dir.reload()
        self.assertEqual(len(test_dir.file_ids), 0)

    def test_02_copy(self):
        test_dir = self.env['ir.filesystem.directory'].create({
            'name': 'Test Orig',
            'directory': gettempdir()
        })

        # test copy
        dir_copy = test_dir.copy()
        self.assertEqual(dir_copy.name, 'Test Orig (copy)')
        self.assertEqual(len(dir_copy.file_ids), test_dir.file_count)
        self.assertEqual(dir_copy.file_count, test_dir.file_count)

    def test_03_not_existing_directory(self):
        test_dir = self.env['ir.filesystem.directory'].create({
            'name': 'Test Not Existing Directory',
            'directory': '/tpd'
        })
        self.assertEqual(len(test_dir.file_ids), 0)
        self.assertEqual(len(test_dir.file_ids), test_dir.file_count)

        # test onchange directory (to existing)
        test_dir.directory = gettempdir()
        self.assertGreaterEqual(len(test_dir.file_ids), 0)
        self.assertEqual(len(test_dir.file_ids), test_dir.file_count)
