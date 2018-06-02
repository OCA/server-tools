# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# Copyright 2018 ACSONE SA/NV.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import os
import tempfile

import mock

from odoo.modules import get_module_path
from odoo.tests import common
from odoo.tests.common import TransactionCase

from ..addon_hash import addon_hash
from ..models.module import IncompleteUpgradeError, DEFAULT_EXCLUDE_PATTERNS

MODULE_NAME = 'module_auto_update'


class TestModule(TransactionCase):

    def setUp(self):
        super(TestModule, self).setUp()
        self.own_module = self.env['ir.module.module'].search([
            ('name', '=', MODULE_NAME),
        ])
        self.own_dir_path = get_module_path(MODULE_NAME)
        keep_langs = self.env['res.lang'].search([]).mapped('code')
        self.own_checksum = addon_hash(
            self.own_dir_path,
            exclude_patterns=DEFAULT_EXCLUDE_PATTERNS.split(','),
            keep_langs=keep_langs,
        )
        self.own_writeable = os.access(self.own_dir_path, os.W_OK)

    def test_compute_checksum_dir(self):
        """It should compute the directory's SHA-1 hash"""
        self.assertEqual(
            self.own_module._get_checksum_dir(), self.own_checksum,
            'Module directory checksum not computed properly',
        )

    def test_compute_checksum_dir_ignore_excluded(self):
        """It should exclude .pyc/.pyo extensions from checksum
        calculations"""
        if not self.own_writeable:
            self.skipTest("Own directory not writeable")
        with tempfile.NamedTemporaryFile(suffix='.pyc', dir=self.own_dir_path):
            self.assertEqual(
                self.own_module._get_checksum_dir(), self.own_checksum,
                'SHA1 checksum does not ignore excluded extensions',
            )

    def test_compute_checksum_dir_recomputes_when_file_added(self):
        """It should return a different value when a non-.pyc/.pyo file is
        added to the module directory"""
        if not self.own_writeable:
            self.skipTest("Own directory not writeable")
        with tempfile.NamedTemporaryFile(suffix='.py', dir=self.own_dir_path):
            self.assertNotEqual(
                self.own_module._get_checksum_dir(), self.own_checksum,
                'SHA1 checksum not recomputed',
            )

    def test_saved_checksums(self):
        Imm = self.env['ir.module.module']
        base_module = Imm.search([('name', '=', 'base')])
        self.assertEqual(base_module.state, 'installed')
        self.assertFalse(Imm._get_saved_checksums())
        Imm._save_installed_checksums()
        saved_checksums = Imm._get_saved_checksums()
        self.assertTrue(saved_checksums)
        self.assertTrue(saved_checksums['base'])

    def test_get_modules_with_changed_checksum(self):
        Imm = self.env['ir.module.module']
        self.assertTrue(Imm._get_modules_with_changed_checksum())
        Imm._save_installed_checksums()
        self.assertFalse(Imm._get_modules_with_changed_checksum())


@common.at_install(False)
@common.post_install(True)
class TestModuleAfterInstall(TransactionCase):

    def setUp(self):
        super(TestModuleAfterInstall, self).setUp()
        Imm = self.env['ir.module.module']
        self.own_module = Imm.search([('name', '=', MODULE_NAME)])
        self.base_module = Imm.search([('name', '=', 'base')])

    def test_get_modules_partially_installed(self):
        Imm = self.env['ir.module.module']
        self.assertTrue(
            self.own_module not in Imm._get_modules_partially_installed())
        self.own_module.button_upgrade()
        self.assertTrue(
            self.own_module in Imm._get_modules_partially_installed())
        self.own_module.button_upgrade_cancel()
        self.assertTrue(
            self.own_module not in Imm._get_modules_partially_installed())

    def test_upgrade_changed_checksum(self):
        Imm = self.env['ir.module.module']
        Bmu = self.env['base.module.upgrade']

        # check modules are in installed state
        installed_modules = Imm.search([('state', '=', 'installed')])
        self.assertTrue(self.own_module in installed_modules)
        self.assertTrue(self.base_module in installed_modules)
        self.assertTrue(len(installed_modules) > 2)
        # change the checksum of 'base'
        Imm._save_installed_checksums()
        saved_checksums = Imm._get_saved_checksums()
        saved_checksums['base'] = False
        Imm._save_checksums(saved_checksums)
        changed_modules = Imm._get_modules_with_changed_checksum()
        self.assertEqual(len(changed_modules), 1)
        self.assertTrue(self.base_module in changed_modules)

        def upgrade_module_mock(self_model):
            upgrade_module_mock.call_count += 1
            # since we are upgrading base, all installed module
            # must have been marked to upgrade at this stage
            self.assertEqual(self.base_module.state, 'to upgrade')
            self.assertEqual(self.own_module.state, 'to upgrade')
            installed_modules.write({'state': 'installed'})

        upgrade_module_mock.call_count = 0

        # upgrade_changed_checksum commits, so mock that
        with mock.patch.object(self.env.cr, 'commit'):

            # we simulate an install by setting module states
            Bmu._patch_method('upgrade_module', upgrade_module_mock)
            try:
                Imm.upgrade_changed_checksum()
                self.assertEqual(upgrade_module_mock.call_count, 1)
                self.assertEqual(self.base_module.state, 'installed')
                self.assertEqual(self.own_module.state, 'installed')
                saved_checksums = Imm._get_saved_checksums()
                self.assertTrue(saved_checksums['base'])
                self.assertTrue(saved_checksums[MODULE_NAME])
            finally:
                Bmu._revert_method('upgrade_module')

    def test_incomplete_upgrade(self):
        Imm = self.env['ir.module.module']
        Bmu = self.env['base.module.upgrade']

        installed_modules = Imm.search([('state', '=', 'installed')])
        # change the checksum of 'base'
        Imm._save_installed_checksums()
        saved_checksums = Imm._get_saved_checksums()
        saved_checksums['base'] = False
        Imm._save_checksums(saved_checksums)

        def upgrade_module_mock(self_model):
            upgrade_module_mock.call_count += 1
            # since we are upgrading base, all installed module
            # must have been marked to upgrade at this stage
            self.assertEqual(self.base_module.state, 'to upgrade')
            self.assertEqual(self.own_module.state, 'to upgrade')
            installed_modules.write({'state': 'installed'})
            # simulate partial upgrade
            self.own_module.write({'state': 'to upgrade'})

        upgrade_module_mock.call_count = 0

        # upgrade_changed_checksum commits, so mock that
        with mock.patch.object(self.env.cr, 'commit'):

            # we simulate an install by setting module states
            Bmu._patch_method('upgrade_module', upgrade_module_mock)
            try:
                with self.assertRaises(IncompleteUpgradeError):
                    Imm.upgrade_changed_checksum()
                self.assertEqual(upgrade_module_mock.call_count, 1)
            finally:
                Bmu._revert_method('upgrade_module')

    def test_incomplete_upgrade_no_checkusm(self):
        Imm = self.env['ir.module.module']
        Bmu = self.env['base.module.upgrade']

        installed_modules = Imm.search(
            [('state', '=', 'installed')])
        # change the checksum of 'base'
        Imm._save_installed_checksums()
        saved_checksums = Imm._get_saved_checksums()

        Imm._save_checksums(saved_checksums)
        self.base_module.write({'state': 'to upgrade'})

        def upgrade_module_mock(self_model):
            upgrade_module_mock.call_count += 1
            # since we are upgrading base, all installed module
            # must have been marked to upgrade at this stage
            self.assertEqual(self.base_module.state, 'to upgrade')
            self.assertEqual(self.own_module.state, 'installed')
            installed_modules.write({'state': 'installed'})

        upgrade_module_mock.call_count = 0

        # upgrade_changed_checksum commits, so mock that
        with mock.patch.object(self.env.cr, 'commit'):

            # we simulate an install by setting module states
            Bmu._patch_method('upgrade_module',
                              upgrade_module_mock)
            # got just other modules to_upgrade and no checksum ones
            try:
                Imm.upgrade_changed_checksum()
                self.assertEqual(upgrade_module_mock.call_count, 1)
            finally:
                Bmu._revert_method('upgrade_module')

    def test_nothing_to_upgrade(self):
        Imm = self.env['ir.module.module']
        Bmu = self.env['base.module.upgrade']

        Imm._save_installed_checksums()

        def upgrade_module_mock(self_model):
            upgrade_module_mock.call_count += 1

        upgrade_module_mock.call_count = 0

        # upgrade_changed_checksum commits, so mock that
        with mock.patch.object(self.env.cr, 'commit'):

            # we simulate an install by setting module states
            Bmu._patch_method('upgrade_module', upgrade_module_mock)
            try:
                Imm.upgrade_changed_checksum()
                self.assertEqual(upgrade_module_mock.call_count, 0)
            finally:
                Bmu._revert_method('upgrade_module')
