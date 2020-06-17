# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from datetime import datetime, timedelta
import json
from werkzeug.contrib.securecookie import SecureCookie
from openerp import _, http, registry, SUPERUSER_ID
from openerp.api import Environment
from openerp.http import Response, request
from openerp.addons.web.controllers.main import Home
from ..exceptions import MfaTokenInvalidError, MfaTokenExpiredError


class JsonSecureCookie(SecureCookie):
    serialization_method = json


class AuthTotp(Home):

    @http.route()
    def web_login(self, *args, **kwargs):
        """Add MFA logic to the web_login action in Home

        Overview:
            * Call web_login in Home
            * Return the result of that call if the user has not logged in yet
              using a password, does not have MFA enabled, or has a valid
              trusted device cookie
            * If none of these is true, generate a new MFA login token for the
              user, log the user out, and redirect to the MFA login form
        """

        # sudo() is required because there may be no request.env.uid (likely
        # since there may be no user logged in at the start of the request)
        user_model_sudo = request.env['res.users'].sudo()
        config_model_sudo = user_model_sudo.env['ir.config_parameter']
        response = super(AuthTotp, self).web_login(*args, **kwargs)

        if request.httprequest.method == 'GET' and not request.session.uid:
            return response

        user = user_model_sudo.browse(request.uid)
        if not user.mfa_enabled:
            return response

        cookie_key = 'trusted_devices_%d' % user.id
        device_cookie = request.httprequest.cookies.get(cookie_key)
        if device_cookie:
            secret = config_model_sudo.get_param('database.secret')
            device_cookie = JsonSecureCookie.unserialize(device_cookie, secret)
            if device_cookie.get('device_id') in user.trusted_device_ids.ids:
                return response

        user.generate_mfa_login_token()
        request.session.logout(keep_db=True)
        return http.local_redirect(
            '/auth_totp/login',
            query={
                'mfa_login_token': user.mfa_login_token,
                'redirect': request.params.get('redirect'),
            },
            keep_hash=True,
        )

    @http.route(
        '/auth_totp/login',
        type='http',
        auth='public',
        methods=['GET'],
        website=True,
    )
    def mfa_login_get(self, *args, **kwargs):
        return request.render('auth_totp.mfa_login', qcontext=request.params)

    @http.route('/auth_totp/login', type='http', auth='none', methods=['POST'])
    def mfa_login_post(self, *args, **kwargs):
        """Process MFA login attempt

        Overview:
            * Try to find a user based on the MFA login token. If this doesn't
              work, redirect to the password login page with an error message
            * Validate the confirmation code provided by the user. If it's not
              valid, redirect to the previous login step with an error message
            * Generate a long-term MFA login token for the user and log the
              user in using the token
            * Build a trusted device cookie and add it to the response if the
              trusted device option was checked
            * Redirect to the provided URL or to '/web' if one was not given
        """

        # sudo() is required because there is no request.env.uid (likely since
        # there is no user logged in at the start of the request)
        user_model_sudo = request.env['res.users'].sudo()
        device_model_sudo = user_model_sudo.env['res.users.device']
        config_model_sudo = user_model_sudo.env['ir.config_parameter']

        token = request.params.get('mfa_login_token')
        try:
            user = user_model_sudo.user_from_mfa_login_token(token)
        except (MfaTokenInvalidError, MfaTokenExpiredError) as exception:
            return http.local_redirect(
                '/web/login',
                query={
                    'redirect': request.params.get('redirect'),
                    'error': exception.message,
                },
                keep_hash=True,
            )

        confirmation_code = request.params.get('confirmation_code')
        if not user.validate_mfa_confirmation_code(confirmation_code):
            return http.local_redirect(
                '/auth_totp/login',
                query={
                    'redirect': request.params.get('redirect'),
                    'error': _(
                        'Your confirmation code is not correct. Please try'
                        ' again.'
                    ),
                    'mfa_login_token': token,
                },
                keep_hash=True,
            )

        # These context managers trigger a safe commit, which persists the
        # changes right away and is needed for the auth call
        with Environment.manage():
            with registry(request.db).cursor() as temp_cr:
                temp_env = Environment(temp_cr, SUPERUSER_ID, request.context)
                temp_user = temp_env['res.users'].browse(user.id)
                temp_user.generate_mfa_login_token(60 * 24 * 30)
                token = temp_user.mfa_login_token
        request.session.authenticate(request.db, user.login, token, user.id)

        redirect = request.params.get('redirect')
        if not redirect:
            redirect = '/web'
        headers = [
            ('Content-Type', 'text/html;charset=utf8')
        ]
        response = Response(
            http.redirect_with_hash(redirect),
            headers=headers,
            status=500
        )

        if request.params.get('remember_device'):
            device = device_model_sudo.create({'user_id': user.id})
            secret = config_model_sudo.get_param('database.secret')
            device_cookie = JsonSecureCookie({'device_id': device.id}, secret)
            cookie_lifetime = timedelta(days=30)
            cookie_exp = datetime.utcnow() + cookie_lifetime
            device_cookie = device_cookie.serialize(cookie_exp)
            cookie_key = 'trusted_devices_%d' % user.id
            sec_config = config_model_sudo.get_param('auth_totp.secure_cookie')
            security_flag = sec_config != '0'
            response.set_cookie(
                cookie_key,
                device_cookie,
                max_age=cookie_lifetime.total_seconds(),
                expires=cookie_exp,
                httponly=True,
                secure=security_flag,
            )

        return response
