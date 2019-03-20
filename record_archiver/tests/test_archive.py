# -*- coding: utf-8 -*-
# © 2015 Guewen Baconnier (Camptocamp SA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import datetime, timedelta
import openerp.tests.common as common


class TestArchive(common.TransactionCase):

    def setUp(self):
        super(TestArchive, self).setUp()
        Partner = self.env['res.partner']
        self.partner1 = Partner.create(
            {'name': 'test user 1'})
        self.partner2 = Partner.create(
            {'name': 'test user 2'})
        self.partner3 = Partner.create(
            {'name': 'test user 3'})
        old_date = datetime.now() - timedelta(days=365)
        self.env.cr.execute(
            'UPDATE res_partner SET write_date = %s '
            'WHERE id IN %s', (old_date, tuple([self.partner2.id,
                                                self.partner3.id]))
        )
        self.Lifespan = self.env['record.lifespan']
        self.model_id = self.ref('base.model_res_partner')

    @common.at_install(False)
    @common.post_install(True)
    def test_lifespan(self):
        lifespan = self.Lifespan.create(
            {'model_id': self.model_id,
             'months': 3,
             })
        lifespan.archive_records()
        self.assertTrue(self.partner1.active)
        self.assertFalse(self.partner2.active)
        self.assertFalse(self.partner3.active)

    @common.at_install(False)
    @common.post_install(True)
    def test_scheduler(self):
        self.Lifespan.create(
            {'model_id': self.model_id,
             'months': 3,
             })
        self.Lifespan._scheduler_archive_records()
        self.assertTrue(self.partner1.active)
        self.assertFalse(self.partner2.active)
        self.assertFalse(self.partner3.active)
