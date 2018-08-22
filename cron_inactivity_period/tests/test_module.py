# coding: utf-8
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestModule(TransactionCase):
    """Tests for 'Cron - Inactivity Period' Module"""

    def setUp(self):
        super(TestModule, self).setUp()
        self.config_obj = self.env['res.config']
        self.cron_obj = self.env['ir.cron']
        self.inactivity_period = self.env['ir.cron.inactivity.period']
        self.vaccum_cron = self.env.ref('base.cronjob_osv_memory_autovacuum')

    # Test Section
    def test_01_no_inactivity_period(self):
        count = self._create_transient_model()
        self.assertEqual(
            count, 0,
            "Calling a cron without inactivity period should run the cron")

    def test_02_no_activity_period(self):
        self.inactivity_period.create({
            'cron_id': self.vaccum_cron.id,
            'type': 'hour',
            'inactivity_hour_begin': 0.0,
            'inactivity_hour_end': 23.59,
        })
        count = self._create_transient_model()
        self.assertEqual(
            count, 1,
            "Calling a cron with inactivity period should not run the cron")

    def _create_transient_model(self):
        self.config_obj.search([]).unlink()
        self.config_obj.create({})
        self.env.cr.execute("update res_config set write_date = '1970-01-01'")
        self.cron_obj._callback(
            'osv_memory.autovacuum', 'power_on', (), self.vaccum_cron.id)
        return len(self.config_obj.search([]))
