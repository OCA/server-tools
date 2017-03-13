# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 GRAP (http://www.grap.coop)
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from lxml import html

from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse

from odoo.tests import common
from odoo.service import wsgi_server


@common.post_install(True)
class TestUI(common.HttpCase):

    def setUp(self):
        super(TestUI, self).setUp()

        with self.registry.cursor() as test_cursor:
            env = self.env(test_cursor)

            self.admin_password = 'AdminPa$$w0rd'
            env.ref('base.user_root').password = self.admin_password
            self.passkey_password = 'PasskeyPa$$w0rd'
            self.passkey_user = env['res.users'].create({
                'name': 'passkey',
                'login': 'passkey',
                'email': 'passkey',
                'password': self.passkey_password
            })
            self.dbname = env.cr.dbname

        self.werkzeug_environ = {'REMOTE_ADDR': '127.0.0.1'}
        self.test_client = Client(wsgi_server.application, BaseResponse)
        self.test_client.get('/web/session/logout')

    def html_doc(self, response):
        """Get an HTML LXML document."""
        return html.fromstring(response.data)

    def csrf_token(self, response):
        """Get a valid CSRF token."""
        doc = self.html_doc(response)
        return doc.xpath("//input[@name='csrf_token']")[0].get('value')

    def get_request(self, url, data=None):
        return self.test_client.get(
            url, query_string=data, follow_redirects=True)

    def post_request(self, url, data=None):
        return self.test_client.post(
            url, data=data, follow_redirects=True,
            environ_base=self.werkzeug_environ)

    def test_01_normal_login_admin_succeed(self):
        # Our admin user wants to go to backoffice part of Odoo
        response = self.get_request('/web/', data={'db': self.dbname})

        # He notices that his redirected to login page as not authenticated
        self.assertIn('oe_login_form', response.data)

        # He needs to enters his credentials and submit the form
        data = {
            'login': 'admin',
            'password': self.admin_password,
            'csrf_token': self.csrf_token(response),
            'db': self.dbname
        }
        response = self.post_request('/web/login/', data=data)

        # He notices that his redirected to backoffice
        self.assertNotIn('oe_login_form', response.data)

    def test_02_normal_login_admin_fail(self):
        # Our admin user wants to go to backoffice part of Odoo
        response = self.get_request('/web/', data={'db': self.dbname})

        # He notices that he's redirected to login page as not authenticated
        self.assertIn('oe_login_form', response.data)

        # He needs to enter his credentials and submit the form
        data = {
            'login': 'admin',
            'password': 'password',
            'csrf_token': self.csrf_token(response),
            'db': self.dbname
        }
        response = self.post_request('/web/login/', data=data)

        # He mistyped his password so he's redirected to login page again
        self.assertIn('Wrong login/password', response.data)

    def test_03_normal_login_passkey_succeed(self):
        # Our passkey user wants to go to backoffice part of Odoo
        response = self.get_request('/web/', data={'db': self.dbname})

        # He notices that he's redirected to login page as not authenticated
        self.assertIn('oe_login_form', response.data)

        # He needs to enter his credentials and submit the form
        data = {
            'login': self.passkey_user.login,
            'password': self.passkey_password,
            'csrf_token': self.csrf_token(response),
            'db': self.dbname
        }
        response = self.post_request('/web/login/', data=data)

        # He notices that his redirected to backoffice
        self.assertNotIn('oe_login_form', response.data)

    def test_04_normal_login_passkey_fail(self):
        # Our passkey user wants to go to backoffice part of Odoo
        response = self.get_request('/web/', data={'db': self.dbname})

        # He notices that he's redirected to login page as not authenticated
        self.assertIn('oe_login_form', response.data)

        # He needs to enter his credentials and submit the form
        data = {
            'login': self.passkey_user.login,
            'password': 'password',
            'csrf_token': self.csrf_token(response),
            'db': self.dbname
        }
        response = self.post_request('/web/login/', data=data)

        # He mistyped his password so he's redirected to login page again
        self.assertIn('Wrong login/password', response.data)

    def test_05_passkey_login_with_admin_password_succeed(self):
        # Our admin user wants to login as passkey user
        response = self.get_request('/web/', data={'db': self.dbname})

        # He notices that his redirected to login page as not authenticated
        self.assertIn('oe_login_form', response.data)

        # He needs to enters its password with passkey user's login
        data = {
            'login': self.passkey_user.login,
            'password': self.admin_password,
            'csrf_token': self.csrf_token(response),
            'db': self.dbname
        }
        response = self.post_request('/web/login/', data=data)

        # He notices that his redirected to backoffice
        self.assertNotIn('oe_login_form', response.data)

    def test_06_passkey_login_with_same_password_as_admin(self):
        self.passkey_user.password = self.admin_password

        # Our passkey user wants to go to backoffice part of Odoo
        response = self.get_request('/web/', data={'db': self.dbname})

        # He notices that his redirected to login page as not authenticated
        self.assertIn('oe_login_form', response.data)

        # He needs to enters his credentials and submit the form
        data = {
            'login': self.passkey_user.login,
            'password': self.admin_password,
            'csrf_token': self.csrf_token(response),
            'db': self.dbname
        }
        response = self.post_request('/web/login/', data=data)

        # He notices that his redirected to backoffice
        self.assertNotIn('oe_login_form', response.data)
