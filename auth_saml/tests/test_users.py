from openerp import SUPERUSER_ID
from openerp.addons.auth_saml.models.base_settings import (
    _SAML_UID_AND_PASS_SETTING)
from openerp.exceptions import ValidationError
from openerp.tests import common
from psycopg2 import IntegrityError


class test_res_users(common.TransactionCase):

    def test_copy(self):
        demo_user = self.env.ref('base.user_demo')
        demo_user.write(
            {'saml_uid': '123',
             'saml_provider_id': self.ref('auth_saml.provider_local')}
        )
        copy = demo_user.copy()
        self.assertFalse(copy.saml_uid)
        self.assertFalse(copy.saml_provider_id)

    def test_unique_saml_uid(self):
        demo_user = self.env.ref('base.user_demo')
        demo_user.write(
            {'saml_uid': '123',
             'saml_provider_id': self.ref('auth_saml.provider_local')}
        )
        copy = demo_user.copy()
        with self.assertRaises(IntegrityError):
            copy.write(
                {'saml_uid': '123',
                 'saml_provider_id': self.ref('auth_saml.provider_local')})

    def test_create_multiple_users_without_saml_provider(self):
        demo_user = self.env.ref('base.user_demo')
        demo_user.copy({'login': '123'})
        demo_user.copy({'login': '456'})

    def test_allow_saml_uid_and_internal_password(self):
        self.env['ir.config_parameter'].set_param(_SAML_UID_AND_PASS_SETTING,
                                                  True)
        demo_user = self.env.ref('base.user_demo')
        demo_user.write(
            {
                'password': "test",
                'saml_uid': "test",
                'saml_provider_id': self.ref('auth_saml.provider_local')
            }
        )

    def test_forbid_saml_uid_and_internal_password(self):
        self.env['ir.config_parameter'].set_param(_SAML_UID_AND_PASS_SETTING,
                                                  False)
        demo_user = self.env.ref('base.user_demo')
        with self.assertRaises(ValidationError):
            demo_user.write(
                {
                    'password': "test",
                    'saml_uid': "test",
                    'saml_provider_id': self.ref('auth_saml.provider_local')
                }
            )
        # except SUPERUSER_ID
        admin = self.env['res.users'].browse(SUPERUSER_ID)
        admin.write(
            {
                'password': "test admin",
                'saml_uid': "test admin",
                'saml_provider_id': self.ref('auth_saml.provider_local')
            }
        )
