# Copyright (C) 2018-Today: Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import hashlib
import mock
from odoo.tests.common import TransactionCase
from ..models.res_users import ResUsers


MODULE_LOCATION = 'odoo.addons.base_user_gravatar.models.res_users'


class TestResUsers(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(TestResUsers, self).setUp()
        self.user_obj = self.env['res.users']
        self.partner_obj = self.env['res.partner']
        config_obj = self.env['ir.config_parameter']
        default_url = "https://www.gravatar.com/avatar/{}?s=200"
        key = "user_gravatar.gravatar_url"
        self.partner_vals = {
            'name': 'Test',
            'email': 'test@example.com',
        }
        self.values = {
            'name': 'Test',
            'login': 'test_login',
        }
        self.gravatar_url = config_obj.get_param(key, default=default_url)

    def _test_record(self):
        """

        :return: res.users recordset
        """
        user_obj = self.user_obj
        partner_obj = self.partner_obj
        partner = partner_obj.create(self.partner_vals)
        self.values.update({
            'partner_id': partner.id,
        })
        return user_obj.create(self.values)

    @mock.patch('%s.urllib' % MODULE_LOCATION)
    def test_get_gravatar_base64_opens_correct_uri(self, magic_mock):
        """
        Test that gravatar is pinged for image
        :param magic_mock: urllib MagicMock object
        :return:
        """
        user_obj = self.user_obj
        gravatar_url = self.gravatar_url
        email = self.partner_vals.get('email', '')
        user_obj._get_gravatar_base64(email)
        expect = hashlib.md5(email.encode('utf-8')).hexdigest()
        magic_mock.request.urlopen.assert_called_once_with(
            gravatar_url.format(expect))

    @mock.patch('%s.base64' % MODULE_LOCATION)
    @mock.patch('%s.urllib' % MODULE_LOCATION)
    def test_get_gravatar_base64_returns_encoded_image(
            self, magic_mock, b64_mk):
        """
        Test that image result is read
        :param magic_mock: urllib MagicMock object
        :param b64_mk: base64 Magic Mock
        :return:
        """
        user_obj = self.user_obj
        email = self.partner_vals.get('email', '')
        expect = 'Expect'
        b64_mk.encodebytes.return_value = expect
        result = user_obj._get_gravatar_base64(email)
        self.assertEquals(expect, result)

    def test_get_gravatar_image_writes_image(self):
        """
        Test that the resulting gravatar is written to user
        :return:
        """
        with mock.patch.object(ResUsers, 'write') as write_mk:
            user = self._test_record()
            with mock.patch.object(user, '_get_gravatar_base64') as mk:
                expect = 'Expect'
                mk.side_effect = ['Fail', expect]
                user.get_gravatar_image()
                write_mk.assert_called_once_with({'image': expect})
