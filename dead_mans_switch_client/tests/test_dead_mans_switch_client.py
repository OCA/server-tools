# © 2015 Therp BV <http://therp.nl>
# © 2017 Avoin.Systems - Miku Laitinen
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tools import mute_logger
from odoo.tests.common import TransactionCase


class TestDeadMansSwitchClient(TransactionCase):
    def test_dead_mans_switch_client(self):
        # test unconfigured case
        self.env['ir.config_parameter'].search([
            ('key', '=', 'dead_mans_switch_client.url')]).unlink()
        with mute_logger(
                'odoo.addons.dead_mans_switch_client.models'
                '.dead_mans_switch_client'
        ):
            self.env['dead.mans.switch.client'].alive()
        # test configured case
        self.env['ir.config_parameter'].set_param(
            'dead_mans_switch_client.url', 'fake_url')
        with self.assertRaises(ValueError):
            self.env['dead.mans.switch.client'].alive()
