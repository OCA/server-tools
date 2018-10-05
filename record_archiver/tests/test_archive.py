# Copyright 2015 Guewen Baconnier (Camptocamp SA)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import datetime, timedelta
import odoo.tests.common as common


class TestArchive(common.SavepointCase):

    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(
            cls.env.context,
            tracking_disable=True,
        ))
        Partner = cls.env['res.partner']
        cls.partner1 = Partner.create(
            {'name': 'test user 1'})
        cls.partner2 = Partner.create(
            {'name': 'test user 2'})
        cls.partner3 = Partner.create(
            {'name': 'test user 3'})
        old_date = datetime.now() - timedelta(days=365)
        cls.env.cr.execute(
            'UPDATE res_partner SET write_date = %s '
            'WHERE id IN %s', (old_date, tuple([cls.partner2.id,
                                                cls.partner3.id]))
        )
        cls.Lifespan = cls.env['record.lifespan']
        cls.model = cls.env.ref('base.model_res_partner')

    def test_lifespan(self):
        lifespan = self.Lifespan.create({
            'model_id': self.model.id,
            'months': 3,
        })
        lifespan.archive_records()
        self.assertTrue(self.partner1.active)
        self.assertFalse(self.partner2.active)
        self.assertFalse(self.partner3.active)

    def test_scheduler(self):
        self.Lifespan.create({
            'model_id': self.model.id,
            'months': 3,
        })
        self.Lifespan._scheduler_archive_records()
        self.assertTrue(self.partner1.active)
        self.assertFalse(self.partner2.active)
        self.assertFalse(self.partner3.active)
