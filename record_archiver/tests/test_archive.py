# Copyright 2015 Guewen Baconnier (Camptocamp SA)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import datetime, timedelta
import odoo.tests.common as common
from odoo.exceptions import ValidationError


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
        Cron = cls.env['ir.cron']  # has both `active` and `state` fields

        cls.Lifespan = cls.env['record.lifespan']
        cls.partner_model = cls.env.ref('base.model_res_partner')
        cls.cron_model = cls.env.ref('base.model_ir_cron')

        cls.partner1 = Partner.create({
            'name': 'test user 1',
        })
        cls.partner2 = Partner.create({
            'name': 'test user 2',
        })
        cls.partner3 = Partner.create({
            'name': 'test user 3',
        })
        cls.cron1 = Cron.create({
            'active': True,
            'model_id': cls.partner_model.id,
            'name': 'Dummy cron 1',
            'state': 'code',
            'code': 'model.browse()',
        })
        cls.cron2 = cls.cron1.copy({
            'name': 'Dummy cron 2',
            'state': 'multi',
        })
        cls.cron3 = cls.cron1.copy({
            'name': 'Dummy cron 3',
            'state': 'object_create',
        })
        old_date = datetime.now() - timedelta(days=365)
        cls.env.cr.execute(
            'UPDATE res_partner SET write_date = %s '
            'WHERE id IN %s', (old_date, (cls.partner2.id, cls.partner3.id))
        )
        cls.env.cr.execute(
            'UPDATE ir_cron SET write_date = %s '
            'WHERE id IN %s', (old_date, (cls.cron2.id, cls.cron3.id)))

    def test_get_archive_states(self):
        # Valid ir.cron states: code, object_create, object_write, multi
        archive_states_valid_variants = [
            'code, multi, object_create',
            'code,multi,object_create',
            'code,multi,object_create,',
            ' code , multi,  object_create',
        ]
        xpected = ['code', 'multi', 'object_create']
        guineapig = self.Lifespan.create({
            'model_id': self.cron_model.id,
            'months': 12,
        })
        for variant in archive_states_valid_variants:
            guineapig.archive_states = variant
            self.assertEqual(guineapig._get_archive_states(), xpected)

    def test_states_constraint_valid(self):
        # Valid ir.cron states: code, object_create, object_write, multi
        self.Lifespan.create({
            'model_id': self.cron_model.id,
            'months': 12,
            'archive_states': 'code',
        })

    def test_states_constraint_invalid(self):
        with self.assertRaises(ValidationError):
            # Valid ir.cron states: code, object_create, object_write, multi
            self.Lifespan.create({
                'model_id': self.cron_model.id,
                'months': 12,
                'archive_states': 'none, of, these, are, valid, states',
            })

    def test_lifespan(self):
        lifespan = self.Lifespan.create({
            'model_id': self.partner_model.id,
            'months': 3,
        })
        lifespan.archive_records()
        self.assertTrue(self.partner1.active)
        self.assertFalse(self.partner2.active)
        self.assertFalse(self.partner3.active)

    def test_lifespan_states(self):
        lifespan = self.Lifespan.create({
            'model_id': self.cron_model.id,
            'months': 3,
            'archive_states': 'code, multi',
        })
        lifespan.archive_records()
        self.assertTrue(self.cron1.active)  # state: code, fresh
        self.assertFalse(self.cron2.active)  # state: multi, fresh
        self.assertTrue(self.cron3.active)  # state: object_create, outdated

    def test_scheduler(self):
        self.Lifespan.create({
            'model_id': self.partner_model.id,
            'months': 3,
        })
        self.Lifespan._scheduler_archive_records()
        self.assertTrue(self.partner1.active)
        self.assertFalse(self.partner2.active)
        self.assertFalse(self.partner3.active)
