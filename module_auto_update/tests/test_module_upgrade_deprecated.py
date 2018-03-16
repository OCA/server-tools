# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import mock

from openerp.modules import get_module_path
from openerp.modules.registry import RegistryManager
from openerp.tests.common import TransactionCase


class TestModuleUpgrade(TransactionCase):

    def setUp(self):
        super(TestModuleUpgrade, self).setUp()
        module_name = 'module_auto_update'
        self.own_module = self.env['ir.module.module'].search([
            ('name', '=', module_name),
        ])
        self.own_dir_path = get_module_path(module_name)

    def test_upgrade_module_cancel(self):
        """It should preserve checksum_installed when cancelling upgrades"""
        self.own_module.write({'state': 'to upgrade'})
        self.own_module.checksum_installed = 'test'
        self.env['base.module.upgrade'].upgrade_module_cancel()
        self.assertEqual(
            self.own_module.checksum_installed, 'test',
            'Upgrade cancellation does not preserve checksum_installed',
        )

    @mock.patch.object(RegistryManager, 'new')
    def test_upgrade_module(self, new_mock):
        """Calls get_module_list when upgrading in api.model mode"""
        get_module_list_mock = mock.MagicMock()
        try:
            self.env['base.module.upgrade']._patch_method(
                'get_module_list',
                get_module_list_mock,
            )
            self.env['base.module.upgrade'].upgrade_module()
            get_module_list_mock.assert_called_once_with()
        finally:
            self.env['base.module.upgrade']._revert_method('get_module_list')
