# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import openerp.tests.common as common
from mock import patch


class TestCronError(common.TransactionCase):

    def setUp(self):

        super(TestCronError, self).setUp()

        cron_obj = self.registry('ir.cron')
        user_obj = self.registry('res.users')

        partner = user_obj.browse(self.cr, self.uid, self.uid).partner_id

        self.cron_id = self.ref('base.cronjob_osv_memory_autovacuum')
        self.cron = cron_obj.browse(self.cr, self.uid, self.cron_id)

        vals = {
                'message_follower_ids': [(4, partner.id)]
                }

        cron_obj.write(self.cr, self.uid, [self.cron_id], vals)
        self.cr.commit()

    def test_00_cron_exception(self):
        cron_obj = self.registry('ir.cron')

        with patch('openerp.addons.base.ir.osv_memory_autovacuum.'
                   'osv_memory_autovacuum.power_on') as power_on_mock:
            power_on_mock.side_effect = Exception('TEST ERROR')

            cron_obj._callback(self.cr, self.cron['user_id'].id,
                               self.cron['model'], self.cron['function'],
                               self.cron['args'], self.cron['id'])

        self.assertEquals(1, len(self.cron.message_ids), 'Should be 1 message')

        self.assertEqual('<p>An error occured during execution of cron %s'
                         ' on DB %s:\n%s</p>' % (self.cron.name,
                                                 self.cr.dbname, 'TEST ERROR'),
                         self.cron.message_ids[0].body)
