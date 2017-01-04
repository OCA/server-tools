# coding: utf-8
# © 2017 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
from ..models.ir_cron import KEEP_ALIVE_CRONS


class TestCron(TransactionCase):

    def test_reactive_cron(self):
        cron_m = self.env['ir.cron']
        # cron creation
        vals = {
            'name': 'Test cron',
        }
        cron = cron_m.create(vals)
        # we now have at least one more cron than in KEEP_ALIVE_CRONS
        # inactive crons
        cron_m._inactive_crons()
        crons = cron_m.search([])
        self.assertEqual(
            len(crons), len(KEEP_ALIVE_CRONS),
            "All crons should be inactive except '%s'" % KEEP_ALIVE_CRONS)
        # active all crons which were active previously
        cron_m._active_previous_crons()
        crons = cron_m.search([])
        self.assertTrue(crons.__contains__(cron),
                        "Cron '%s' should be activate" % cron.name)
