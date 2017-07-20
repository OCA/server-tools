# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import mock

from odoo.modules import get_module_path
from odoo.modules.registry import Registry
from odoo.tests.common import TransactionCase


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

    @mock.patch.object(Registry, 'new')
    def test_upgrade_module(self, new_mock):
        """It should call update_list method on ir.module.module"""
        update_list_mock = mock.MagicMock()
        self.env['ir.module.module']._patch_method(
            'update_list',
            update_list_mock,
        )
        self.env['base.module.upgrade'].upgrade_module()
        update_list_mock.assert_called_once_with()
        self.env['ir.module.module']._revert_method('update_list')
