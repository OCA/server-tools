# © 2015 Therp BV <http://therp.nl>
# © 2017 Avoin.Systems - Miku Laitinen
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger

from ..models.dead_mans_switch_client import DMSFilterException


class TestDeadMansSwitchClient(TransactionCase):
    def test_dead_mans_switch_client(self):
        # test unconfigured case
        self.env["ir.config_parameter"].search(
            [("key", "=", "dead_mans_switch_client.url")]
        ).unlink()
        with mute_logger(
            "odoo.addons.dead_mans_switch_client.models" ".dead_mans_switch_client"
        ):
            self.env["dead.mans.switch.client"].alive()
        # test configured case
        self.env["ir.config_parameter"].set_param(
            "dead_mans_switch_client.url", "fake_url"
        )
        with self.assertRaises(ValueError):
            self.env["dead.mans.switch.client"].alive()

    def test_dead_mans_switch_client_filters(self):

        # Seriosly, looking for failed outgoing emails would be a better
        # example, but I don't want to add a module dependency only because
        # of a single unit test.

        self.assertTrue(
            self.env["res.partner"].search([("name", "=", "Marc Demo")]),
            msg="A partner named Marc Demo should exist in the demo data",
        )
        self.env["ir.filters"].create(
            {
                "name": "Marc",
                "model_id": "res.partner",
                "domain": "[('name', '=', 'Marc Demo')]",
                "is_dead_mans_switch_filter": True,
            }
        )

        self.assertFalse(
            self.env["res.partner"].search([("name", "=", "Nimrod Soames")]),
            msg="A partner named Nimrod Soames should not exist in the demo data",
        )
        self.env["ir.filters"].create(
            {
                "name": "Nimmy",
                "model_id": "res.partner",
                "domain": "[('name', '=', 'Nimrod Soames')]",
                "is_dead_mans_switch_filter": True,
            }
        )

        with self.assertRaises(DMSFilterException):
            self.env["dead.mans.switch.client"].alive()
