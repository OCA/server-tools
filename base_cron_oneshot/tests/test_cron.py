# Copyright (C) 2018 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint disable=anomalous-backslash-in-string

from odoo import api
from odoo.tests import common

import datetime
import mock


MOCK_PATH = 'odoo.addons.base_cron_oneshot.models.ir_cron'


class OneshotTestCase(common.SavepointCase):

    @property
    def cron_model(self):
        return self.env['ir.cron']

    @mock.patch(MOCK_PATH + '.datetime')
    def test_defaults(self, mocked_dt):
        mocked_dt.now.return_value = datetime.datetime(2018, 8, 31, 10, 30)
        cron = self.cron_model.create({
            'oneshot': True,
            'name': 'Foo',
            'model_id': self.env['ir.model']._get('ir.cron').id,
            'state': 'code',
            'code': 'model.some_method()',
            'interval_number': 1,
            'interval_type': 'days',
            'numbercall': 5,  # won't have any effect
        })
        self.assertRegexpMatches(cron.name, 'Oneshot#\d+ Foo')
        self.assertEqual(cron.numbercall, 1)
        # call postponed by 10mins
        self.assertEqual(cron.nextcall, '2018-08-31 10:40:00')

    def test_schedule_oneshot_check(self):
        with self.assertRaises(AssertionError) as err:
            self.cron_model.schedule_oneshot('res.partner')
        self.assertEqual(str(err.exception), 'Provide a method or some code!')

    @mock.patch(MOCK_PATH + '.datetime')
    def test_schedule_oneshot_method(self, mocked_dt):
        mocked_dt.now.return_value = datetime.datetime(2018, 8, 31, 16, 30)
        cron = self.cron_model.schedule_oneshot(
            'res.partner', method='read', delay=('minutes', 30))
        self.assertRegexpMatches(cron.name, 'Oneshot#\d+')
        self.assertEqual(cron.numbercall, 1)
        self.assertEqual(cron.code, 'model.read()')
        self.assertEqual(
            cron.model_id, self.env['ir.model']._get('res.partner'))
        self.assertEqual(cron.nextcall, '2018-08-31 17:00:00')

    def test_schedule_oneshot_code(self):
        cron = self.cron_model.schedule_oneshot(
            'res.partner', code='env["res.partner"].search([])')
        self.assertRegexpMatches(cron.name, 'Oneshot#\d+')
        self.assertEqual(cron.numbercall, 1)
        self.assertEqual(cron.state, 'code')
        self.assertEqual(cron.code, 'env["res.partner"].search([])')
        self.assertEqual(
            cron.model_id, self.env['ir.model']._get('res.partner'))


class OneshotProcessTestCase(common.TransactionCase):

    def setUp(self):
        super().setUp()
        deleted = []

        @api.multi
        def unlink(self):
            deleted.extend(self.ids)
            # do nothing as the original one will try to read the lock
            # for the current record which is NOT committed
            # and has no real ID.
            return

        self.env['ir.cron']._patch_method('unlink', unlink)
        self.addCleanup(self.env['ir.cron']._revert_method, 'unlink')
        self.deleted = deleted

    def test_schedule_oneshot_cleanup(self):
        cron1 = self.env['ir.cron'].schedule_oneshot(
            'res.partner', code='env["res.partner"].search([])')
        cron2 = self.env['ir.cron'].schedule_oneshot(
            'res.partner', code='env["res.partner"].read([])')
        # simulate excuted
        cron1.write({'numbercall': 0, 'active': False})
        self.env['ir.cron'].cron_oneshot_cleanup()
        self.assertIn(cron1.id, self.deleted)
        self.assertNotIn(cron2.id, self.deleted)
