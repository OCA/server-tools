# © 2015 Therp BV <http://therp.nl>
# © 2017 Avoin.Systems - Miku Laitinen
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from unittest import mock

from odoo.tests.common import TransactionCase


class TestDeadMansSwitchClient(TransactionCase):
    def test_dead_mans_switch_client(self):
        # test unconfigured case
        self.env['ir.config_parameter'].search([
            ('key', '=', 'dead_mans_switch_client.url')]).unlink()
        with mock.patch(
            "odoo.addons.dead_mans_switch_client.models"
            ".dead_mans_switch_client._logger"
        ) as logger:
            self.env['dead.mans.switch.client'].alive()
        logger.error.assert_called_with("No server configured!")

        # test configured case
        self.env['ir.config_parameter'].set_param(
            'dead_mans_switch_client.url', 'fake_url')
        with mock.patch("requests.post") as post:
            self.env['dead.mans.switch.client'].alive()
        args, kwargs = post.call_args

        self.assertEqual(args, ("fake_url",))
        data = kwargs["json"]
        self.assertEqual(
            data["params"]["database_uuid"],
            self.env["ir.config_parameter"].get_param("database.uuid"),
        )
        self.assertEqual(len(data["params"]["database_uuid"]), 36)
        self.assertEqual(
            set(data["params"].keys()),
            {"database_uuid", "cpu", "ram", "user_count"},
        )
