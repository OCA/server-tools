# -*- coding: utf-8 -*-

from openerp.tests.common import TransactionCase


class TestUserMaintenanceMode(TransactionCase):

    def setUp(self):
        super(TestUserMaintenanceMode, self).setUp()
        self.partner = self.env.ref('base.res_partner_2')
        vals = {
            'name': 'Test User Maintenance Mode',
            'login': 'test_user_maintenance_mode',
            'password': 'test_user_maintenance_mode',
            'partner_id': self.partner.id,
        }
        self.user = self.env['res.users'].create(vals)

    def test_user_maintenance_mode(self):
        self.wizard = self.env['change.maintenance.mode.wizard'].create({})
        self.wizard.with_context({'active_ids': [self.user.id]}) \
            .select_maintenance_mode()
        self.assertEqual(self.user.maintenance_mode, True)
        self.wizard = self.env['change.maintenance.mode.wizard'].create({})
        self.wizard.with_context({'active_ids': [self.user.id]}) \
            .unselect_maintenance_mode()
        self.assertEqual(self.user.maintenance_mode, False)
