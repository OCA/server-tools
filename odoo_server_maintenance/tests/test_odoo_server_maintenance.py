# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase


class TestOdooServerMaintenance(TransactionCase):

    def setUp(self):
        super(TestOdooServerMaintenance, self).setUp()
        self.partner = self.env.ref('base.res_partner_2')
        vals = {
            'name': 'Test Odoo Server Maintenance',
            'login': 'test_odoo_server_maintenance',
            'password': 'test_odoo_server_maintenance',
            'partner_id': self.partner.id,
        }
        self.user = self.env['res.users'].create(vals)

    def test_odoo_server_maintenance(self):
        self.wizard = self.env['change.maintenance.mode.wizard'].create({})
        self.wizard.with_context({'active_ids': [self.user.id]}) \
            .select_maintenance_mode()
        self.assertEqual(self.user.maintenance_mode, True)
        self.wizard = self.env['change.maintenance.mode.wizard'].create({})
        self.wizard.with_context({'active_ids': [self.user.id]}) \
            .unselect_maintenance_mode()
        self.assertEqual(self.user.maintenance_mode, False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
