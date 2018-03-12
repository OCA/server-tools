# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
import os
import tempfile

import mock

from odoo.modules import get_module_path
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger

from .. import post_init_hook

_logger = logging.getLogger(__name__)
try:
    from checksumdir import dirhash
except ImportError:
    _logger.debug('Cannot `import checksumdir`.')

model = 'openerp.addons.module_checksum_upgrade.models.module'


class EndTestException(Exception):
    pass


class TestModule(TransactionCase):

    def setUp(self):
        super(TestModule, self).setUp()
        module_name = 'module_auto_update'
        self.own_module = self.env['ir.module.module'].search([
            ('name', '=', module_name),
        ])
        self.own_dir_path = get_module_path(module_name)
        self.own_checksum = dirhash(
            self.own_dir_path,
            'sha1',
            excluded_extensions=['pyc', 'pyo'],
        )
        self.own_writeable = os.access(self.own_dir_path, os.W_OK)

    @mock.patch('%s.get_module_path' % model)
    def create_test_module(self, vals, get_module_path_mock):
        get_module_path_mock.return_value = self.own_dir_path
        test_module = self.env['ir.module.module'].create(vals)
        return test_module

    def test_compute_checksum_dir(self):
        """It should compute the directory's SHA-1 hash"""
        self.assertEqual(
            self.own_module.checksum_dir, self.own_checksum,
            'Module directory checksum not computed properly',
        )

    def test_compute_checksum_dir_ignore_excluded(self):
        """It should exclude .pyc/.pyo extensions from checksum
        calculations"""
        if not self.own_writeable:
            self.skipTest("Own directory not writeable")
        with tempfile.NamedTemporaryFile(
                suffix='.pyc', dir=self.own_dir_path):
            self.assertEqual(
                self.own_module.checksum_dir, self.own_checksum,
                'SHA1 checksum does not ignore excluded extensions',
            )

    def test_compute_checksum_dir_recomputes_when_file_added(self):
        """It should return a different value when a non-.pyc/.pyo file is
        added to the module directory"""
        if not self.own_writeable:
            self.skipTest("Own directory not writeable")
        with tempfile.NamedTemporaryFile(
                suffix='.py', dir=self.own_dir_path):
            self.assertNotEqual(
                self.own_module.checksum_dir, self.own_checksum,
                'SHA1 checksum not recomputed',
            )

    def test_store_checksum_installed_state_installed(self):
        """It should set the module's checksum_installed equal to
        checksum_dir when vals contain a ``latest_version`` str."""
        self.own_module.checksum_installed = 'test'
        self.own_module._store_checksum_installed({'latest_version': '1.0'})
        self.assertEqual(
            self.own_module.checksum_installed, self.own_module.checksum_dir,
        )

    def test_store_checksum_installed_state_uninstalled(self):
        """It should clear the module's checksum_installed when vals
        contain ``"latest_version": False``"""
        self.own_module.checksum_installed = 'test'
        self.own_module._store_checksum_installed({'latest_version': False})
        self.assertIs(self.own_module.checksum_installed, False)

    def test_store_checksum_installed_vals_contain_checksum_installed(self):
        """It should not set checksum_installed to False or checksum_dir when
        a checksum_installed is included in vals"""
        self.own_module.checksum_installed = 'test'
        self.own_module._store_checksum_installed({
            'state': 'installed',
            'checksum_installed': 'test',
        })
        self.assertEqual(
            self.own_module.checksum_installed, 'test',
            'Providing checksum_installed in vals did not prevent overwrite',
        )

    def test_store_checksum_installed_with_retain_context(self):
        """It should not set checksum_installed to False or checksum_dir when
        self has context retain_checksum_installed=True"""
        self.own_module.checksum_installed = 'test'
        self.own_module.with_context(
            retain_checksum_installed=True,
        )._store_checksum_installed({'state': 'installed'})
        self.assertEqual(
            self.own_module.checksum_installed, 'test',
            'Providing retain_checksum_installed context did not prevent '
            'overwrite',
        )

    @mock.patch('%s.get_module_path' % model)
    def test_button_uninstall_no_recompute(self, module_path_mock):
        """It should not attempt update on `button_uninstall`."""
        module_path_mock.return_value = self.own_dir_path
        vals = {
            'name': 'module_auto_update_test_module',
            'state': 'installed',
        }
        test_module = self.create_test_module(vals)
        test_module.checksum_installed = 'test'
        uninstall_module = self.env['ir.module.module'].search([
            ('name', '=', 'web'),
        ])
        uninstall_module.button_uninstall()
        self.assertNotEqual(
            test_module.state, 'to upgrade',
            'Auto update logic was triggered during uninstall.',
        )

    def test_button_immediate_uninstall_no_recompute(self):
        """It should not attempt update on `button_immediate_uninstall`."""

        uninstall_module = self.env['ir.module.module'].search([
            ('name', '=', 'web'),
        ])

        try:
            mk = mock.MagicMock()
            uninstall_module._patch_method('button_uninstall', mk)
            mk.side_effect = EndTestException
            with self.assertRaises(EndTestException):
                uninstall_module.button_immediate_uninstall()
        finally:
            uninstall_module._revert_method('button_uninstall')

    def test_button_uninstall_cancel(self):
        """It should preserve checksum_installed when cancelling uninstall"""
        self.own_module.write({'state': 'to remove'})
        self.own_module.checksum_installed = 'test'
        self.own_module.button_uninstall_cancel()
        self.assertEqual(
            self.own_module.checksum_installed, 'test',
            'Uninstall cancellation does not preserve checksum_installed',
        )

    def test_button_upgrade_cancel(self):
        """It should preserve checksum_installed when cancelling upgrades"""
        self.own_module.write({'state': 'to upgrade'})
        self.own_module.checksum_installed = 'test'
        self.own_module.button_upgrade_cancel()
        self.assertEqual(
            self.own_module.checksum_installed, 'test',
            'Upgrade cancellation does not preserve checksum_installed',
        )

    def test_create(self):
        """It should call _store_checksum_installed method"""
        _store_checksum_installed_mock = mock.MagicMock()
        self.env['ir.module.module']._patch_method(
            '_store_checksum_installed',
            _store_checksum_installed_mock,
        )
        vals = {
            'name': 'module_auto_update_test_module',
            'state': 'installed',
        }
        self.create_test_module(vals)
        _store_checksum_installed_mock.assert_called_once_with(vals)
        self.env['ir.module.module']._revert_method(
            '_store_checksum_installed',
        )

    @mute_logger("openerp.modules.module")
    @mock.patch('%s.get_module_path' % model)
    def test_get_module_list(self, module_path_mock):
        """It should change the state of modules with different
        checksum_dir and checksum_installed to 'to upgrade'"""
        module_path_mock.return_value = self.own_dir_path
        vals = {
            'name': 'module_auto_update_test_module',
            'state': 'installed',
        }
        test_module = self.create_test_module(vals)
        test_module.checksum_installed = 'test'
        self.env['base.module.upgrade'].get_module_list()
        self.assertEqual(
            test_module.state, 'to upgrade',
            'List update does not mark upgradeable modules "to upgrade"',
        )

    @mock.patch('%s.get_module_path' % model)
    def test_get_module_list_only_changes_installed(self, module_path_mock):
        """It should not change the state of a module with a former state
        other than 'installed' to 'to upgrade'"""
        module_path_mock.return_value = self.own_dir_path
        vals = {
            'name': 'module_auto_update_test_module',
            'state': 'uninstalled',
        }
        test_module = self.create_test_module(vals)
        self.env['base.module.upgrade'].get_module_list()
        self.assertNotEqual(
            test_module.state, 'to upgrade',
            'List update changed state of an uninstalled module',
        )

    def test_write(self):
        """It should call _store_checksum_installed method"""
        _store_checksum_installed_mock = mock.MagicMock()
        self.env['ir.module.module']._patch_method(
            '_store_checksum_installed',
            _store_checksum_installed_mock,
        )
        vals = {'state': 'installed'}
        self.own_module.write(vals)
        _store_checksum_installed_mock.assert_called_once_with(vals)
        self.env['ir.module.module']._revert_method(
            '_store_checksum_installed',
        )

    def test_post_init_hook(self):
        """It should set checksum_installed equal to checksum_dir for all
        installed modules"""
        installed_modules = self.env['ir.module.module'].search([
            ('state', '=', 'installed'),
        ])
        post_init_hook(self.env.cr, None)
        self.assertListEqual(
            installed_modules.mapped('checksum_dir'),
            installed_modules.mapped('checksum_installed'),
            'Installed modules did not have checksum_installed stored',
        )
