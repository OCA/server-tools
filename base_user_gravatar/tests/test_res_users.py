# -*- coding: utf-8 -*-
# © 2016-TODAY LasLabs, Inc. [https://laslabs.com]
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
from ..models.res_users import ResUsers
import mock
import hashlib


MODULE_LOCATION = 'openerp.addons.base_user_gravatar.models.res_users'


class TestResUsers(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(TestResUsers, self).setUp()
        self.model_obj = self.env['res.users']
        self.partner_vals = {
            'name': 'Test',
            'email': 'test@example.com',
        }
        self.vals = {
            'name': 'Test',
            'login': 'test_login',
        }
        self.url = 'http://www.gravatar.com/avatar/{}?s=200'

    def _test_record(self, ):
        partner_id = self.env['res.partner'].create(self.partner_vals)
        self.vals['partner_id'] = partner_id.id
        return self.env['res.users'].create(self.vals)

    @mock.patch('%s.urllib2' % MODULE_LOCATION)
    def test_get_gravatar_base64_opens_correct_uri(self, mk, ):
        """ Test that gravatar is pinged for image """
        self.model_obj._get_gravatar_base64(self.partner_vals['email'])
        expect = hashlib.md5(self.partner_vals['email']).hexdigest()
        mk.urlopen.assert_called_once_with(self.url.format(expect))

    @mock.patch('%s.base64' % MODULE_LOCATION)
    @mock.patch('%s.urllib2' % MODULE_LOCATION)
    def test_get_gravatar_base64_returns_encoded_image(self, mk, b64_mk, ):
        """ Test that image result is read """
        expect = 'Expect'
        b64_mk.encodestring.return_value = expect
        result = self.model_obj._get_gravatar_base64(
            self.partner_vals['email']
        )
        self.assertEquals(expect, result)

    def test_get_gravatar_image_writes_image(self, ):
        """ Test that the resulting gravatar is written to user """
        with mock.patch.object(ResUsers, 'write') as write_mk:
            user_id = self._test_record()
            with mock.patch.object(user_id, '_get_gravatar_base64') as mk:
                expect = 'Expect'
                mk.side_effect = ['Fail', expect]
                user_id.get_gravatar_image()
                write_mk.assert_called_once_with({'image': expect})

    def test_compute_gravatar_autoupdate_enabled(self, ):
        """Update computed module"""
        IrParameter = self.env['ir.config.parameter']
        IrParameter.set_param('gravatar.autoupdate', False)
        user_id = self._test_record()
        user_id.recompute()
        self.assertEquals(False, user_id.gravatar_autoupdate_enabled)
        IrParameter.set_param('gravatar.autoupdate', True)
        user_id.recompute()
        self.assertEquals(True, user_id.gravatar_autoupdate_enabled)

    def test_update_gravatars(self, ):
        """Tests cron"""
        result = self.model_obj._update_gravatars()
        self.assertEquals(True, result)
