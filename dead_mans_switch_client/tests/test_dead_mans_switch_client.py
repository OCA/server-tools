# -*- coding: utf-8 -*-
# © 2015 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.tools.misc import mute_logger
from openerp.tests.common import TransactionCase


class TestDeadMansSwitchClient(TransactionCase):
    def test_dead_mans_switch_client(self):
        # test unconfigured case
        self.env['ir.config_parameter'].search([
            ('key', '=', 'dead_mans_switch_client.url')]).unlink()
        logger = ('openerp.addons.dead_mans_switch_client.models'
                  '.dead_mans_switch_client')
        with mute_logger(logger):
            self.env['dead.mans.switch.client'].alive()
        # test configured case
        self.env['ir.config_parameter'].set_param(
            'dead_mans_switch_client.url', 'fake_url')
        with self.assertRaises(ValueError):
            self.env['dead.mans.switch.client'].alive()
