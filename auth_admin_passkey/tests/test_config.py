# -*- coding: utf-8 -*-
# Copyright 2019 Therp BV (https://therp.nl)
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
from odoo.tests import common


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
        self.assertEqual(
            False,
            config_model.get_default_auth_admin_passkey_send_to_admin([])[
                "auth_admin_passkey_send_to_admin"
            ],
        )
        self.assertEqual(
            False,
            config_model.get_default_auth_admin_passkey_send_to_user([])[
                "auth_admin_passkey_send_to_user"
            ],
        )
        config.write(
            {
                "auth_admin_passkey_send_to_admin": True,
                "auth_admin_passkey_send_to_user": True,
            }
        )
        config.set_auth_admin_passkey_send_to_admin()
        config.set_auth_admin_passkey_send_to_user()
        self.assertEqual(
            u'True',
            config_model.get_default_auth_admin_passkey_send_to_admin([])[
                "auth_admin_passkey_send_to_admin"
            ],
        )
        self.assertEqual(
            u'True',
            config_model.get_default_auth_admin_passkey_send_to_user([])[
                "auth_admin_passkey_send_to_user"
            ],
        )
