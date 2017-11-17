# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

from mock import patch
import os
import sys
from odoo.modules.module import get_module_path
from odoo.tests.common import TransactionCase

module_path = get_module_path('auth_totp')
migration_path = os.path.join(module_path, 'migrations', '10.0.2.0.0')
sys.path.insert(0, migration_path)
sys.modules.pop('auth_totp', None)
post_migrate = __import__('post-migrate')
migrate = post_migrate.migrate

HELPER_PATH = 'odoo.addons.base.ir.ir_model.IrModelFields._prepare_update'


@patch(HELPER_PATH, autospec=True)
class TestPostMigrate(TransactionCase):
    def setUp(self):
        super(TestPostMigrate, self).setUp()

        self.test_user = self.env['res.users'].create({
            'name': 'Test User',
            'login': 'test_user',
        })
        self.env['res.users.authenticator'].create({
            'name': 'Test Name',
            'secret_key': 'Test Key',
            'user_id': self.test_user.id,
        })
        self.test_user.mfa_enabled = True
        self.test_user.active = False

        self.test_user_2 = self.env['res.users'].create({
            'name': 'Test User 2',
            'login': 'test_user_2',
        })

        self.test_device_model = self.env['ir.model'].create({
            'name': 'Test Device Model',
            'model': 'res.users.device',
            'state': 'base',
        })

    def test_migrate_mfa_enabled(self, helper_mock):
        """It should give users with MFA enabled a new key"""
        old_key = self.test_user.trusted_device_cookie_key
        migrate(self.env.cr, None)

        self.assertTrue(self.test_user.trusted_device_cookie_key)
        self.assertNotEqual(self.test_user.trusted_device_cookie_key, old_key)

    def test_migrate_mfa_disabled(self, helper_mock):
        """It should leave users with MFA disabled without a key"""
        migrate(self.env.cr, None)

        self.assertFalse(self.test_user_2.trusted_device_cookie_key)

    def test_migrate_call_field_helper(self, helper_mock):
        """It should call update helper on all device model field records"""
        test_field = self.test_device_model.field_id
        test_field_2 = self.env['ir.model.fields'].create({
            'name': 'test_field_2',
            'model': self.test_device_model.model,
            'model_id': self.test_device_model.id,
            'ttype': 'char',
            'state': 'base',
        })
        test_field_set = test_field + test_field_2
        migrate(self.env.cr, None)

        helper_mock.assert_called_once_with(test_field_set)

    def test_migrate_clean_up_constraints(self, helper_mock):
        """It should clean up all constraints associated with device model"""
        test_module_record = self.env['ir.module.module'].search([], limit=1)
        self.env['ir.model.constraint'].create({
            'name': 'Test Constraint',
            'model': self.test_device_model.id,
            'module': test_module_record.id,
            'type': 'u',
        })
        self.env['ir.model.constraint'].create({
            'name': 'Test Constraint 2',
            'model': self.test_device_model.id,
            'module': test_module_record.id,
            'type': 'u',
        })
        migrate(self.env.cr, None)

        resulting_constraints = self.env['ir.model.constraint'].search([
            ('model', '=', self.test_device_model.id),
        ])
        self.assertFalse(resulting_constraints)

    def test_migrate_clean_up_xml_ids(self, helper_mock):
        """It should clean up XML IDs tied to device model"""
        self.env['ir.model.data'].create({
            'name': 'Test XML ID',
            'model': 'ir.model',
            'res_id': self.test_device_model.id,
        })
        self.env['ir.model.data'].create({
            'name': 'Test XML ID 2',
            'model': 'ir.model',
            'res_id': self.test_device_model.id,
        })
        migrate(self.env.cr, None)

        resulting_xml_ids = self.env['ir.model.data'].search([
            ('model', '=', 'ir.model'),
            ('res_id', '=', self.test_device_model.id),
        ])
        self.assertFalse(resulting_xml_ids)

    def test_migrate_clean_up_ir_record(self, helper_mock):
        """It should clean up device model ir.model record"""
        migrate(self.env.cr, None)

        self.assertFalse(self.test_device_model.exists())
