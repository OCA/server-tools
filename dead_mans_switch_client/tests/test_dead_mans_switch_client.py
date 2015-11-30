# -*- coding: utf-8 -*-
# © 2015 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.tests.common import TransactionCase


class TestDeadMansSwitchClient(TransactionCase):
    def test_dead_mans_switch_client(self):
        # test unconfigured case
        ir_config_parameter = self.registry('ir.config_parameter')
        ir_config_parameter.unlink(
            self.cr, self.uid,
            ir_config_parameter.search(
                self.cr, self.uid,
                [('key', '=', 'dead_mans_switch_client.url')]))
        dead_mans_switch_client = self.registry('dead.mans.switch.client')
        dead_mans_switch_client.alive(self.cr, self.uid)
        # test configured case
        ir_config_parameter.set_param(
            self.cr, self.uid, 'dead_mans_switch_client.url', 'fake_url')
        with self.assertRaises(ValueError):
            dead_mans_switch_client.alive(self.cr, self.uid)
