# coding: utf-8
# © 2017 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestCron(TransactionCase):

    def test_reactive_cron(self):
        cron_m = self.env['ir.cron']
        # cron creation
        vals = {
            'name': 'Test cron',
        }
        cron = cron_m.create(vals)
        # inactive
        cron_m._inactive_crons()
        crons = cron_m.search([])
        self.assertEqual(len(crons), 0, "All crons should be inactive")
        cron_m._active_previous_crons()
        crons = cron_m.search([])
        self.assertTrue(cron in [x for x in crons],
                        "Cron '%s' should be activate" % cron.name)
