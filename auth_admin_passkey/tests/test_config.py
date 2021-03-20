# -*- coding: utf-8 -*-
# Copyright 2019 Therp BV (https://therp.nl)
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
import logging

from odoo.tests import common

_logger = logging.getLogger(__name__)


@common.post_install(True)
class TestConfig(common.TransactionCase):
    def test_set_get_config(self):
        """Test configuration methods."""
        config_model = self.env["base.config.settings"]
        config = config_model.create(
            {
                "auth_admin_passkey_send_to_admin": False,
                "auth_admin_passkey_send_to_user": False,
            }
        )
        # Set email admin and user to False (and back again).
        config.set_auth_admin_passkey_send_to_admin()
        config.set_auth_admin_passkey_send_to_user()
        self.assertFalse(config.auth_admin_passkey_send_to_admin)
        self.assertFalse(config.auth_admin_passkey_send_to_user)
        self.assertFalse(
            config_model.get_default_auth_admin_passkey_send_to_admin([])[
                "auth_admin_passkey_send_to_admin"
            ]
        )
        self.assertFalse(
            config_model.get_default_auth_admin_passkey_send_to_user([])[
                "auth_admin_passkey_send_to_user"
            ]
        )
        config.write(
            {
                "auth_admin_passkey_send_to_admin": True,
                "auth_admin_passkey_send_to_user": True,
            }
        )
        config.set_auth_admin_passkey_send_to_admin()
        config.set_auth_admin_passkey_send_to_user()
        self.assertTrue(config.auth_admin_passkey_send_to_admin)
        self.assertTrue(config.auth_admin_passkey_send_to_user)
        self.assertTrue(
            config_model.get_default_auth_admin_passkey_send_to_admin([])[
                "auth_admin_passkey_send_to_admin"
            ]
        )
        self.assertTrue(
            config_model.get_default_auth_admin_passkey_send_to_user([])[
                "auth_admin_passkey_send_to_user"
            ]
        )

    def test_read_legacy_config_values(self):
        """ Make sure that any falsy or truthy value formats that were
            used in past, are still interpreted as such """
        config_model = self.env["base.config.settings"]
        param_model = self.env["ir.config_parameter"]

        values = {False: ["False", "0", "", "None", None], True: ["True", "1"]}

        for boolean_value, char_values in values.iteritems():
            for char_value in char_values:
                _logger.info(
                    "Testing for value %s, type %s", char_value, type(char_value)
                )
                param_model.set_param("auth_admin_passkey.send_to_admin", char_value)
                param_model.set_param("auth_admin_passkey.send_to_user", char_value)
                config = config_model.create({})
                self.assertEqual(boolean_value, config.auth_admin_passkey_send_to_admin)
                self.assertEqual(boolean_value, config.auth_admin_passkey_send_to_user)
