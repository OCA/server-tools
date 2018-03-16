# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import os

import mock

from openerp.modules import get_module_path
from openerp.tests.common import TransactionCase
from openerp.tools import mute_logger

from openerp.addons.module_auto_update.addon_hash import addon_hash

from ..models.module_deprecated import PARAM_DEPRECATED


model = 'openerp.addons.module_auto_update.models.module'


class TestModule(TransactionCase):

    def setUp(self):
        super(TestModule, self).setUp()
        module_name = 'module_auto_update'
        self.env["ir.config_parameter"].set_param(PARAM_DEPRECATED, "1")
        self.own_module = self.env['ir.module.module'].search([
            ('name', '=', module_name),
        ])
        self.own_dir_path = get_module_path(module_name)
        keep_langs = self.env['res.lang'].search([]).mapped('code')
        self.own_checksum = addon_hash(
            self.own_dir_path,
            exclude_patterns=['*.pyc', '*.pyo', '*.pot', 'static/*'],
            keep_langs=keep_langs,
        )
        self.own_writeable = os.access(self.own_dir_path, os.W_OK)

    @mock.patch('%s.get_module_path' % model)
    def create_test_module(self, vals, get_module_path_mock):
        get_module_path_mock.return_value = self.own_dir_path
        test_module = self.env['ir.module.module'].create(vals)
        return test_module

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
        try:
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
        finally:
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
