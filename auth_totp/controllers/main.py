# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta
import json
from werkzeug.contrib.securecookie import SecureCookie
from openerp import http, registry, SUPERUSER_ID
from openerp.api import Environment
from openerp.http import Response, request
from openerp.addons.web.controllers.main import Home
from ..exceptions import MfaTokenInvalidError, MfaTokenExpiredError


class JsonSecureCookie(SecureCookie):
    serialization_method = json


class AuthTotp(Home):
    @http.route()
    def web_login(self, *args, **kwargs):
        response = super(AuthTotp, self).web_login(*args, **kwargs)

        if not request.params.get('login_success'):
            return response

        user = request.env['res.users'].sudo().browse(request.uid)
        if not user.mfa_enabled:
            return response

        cookie_key = 'trusted_devices_%s' % user.id
        device_cookie = request.httprequest.cookies.get(cookie_key)
        if device_cookie:
            config_model = request.env['ir.config_parameter']
            secret = config_model.sudo().get_param('database.secret')
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

    @http.route('/auth_totp/login', type='http', auth='none', methods=['GET'])
    def mfa_login_form(self, *args, **kwargs):
        return request.render('auth_totp.mfa_login', qcontext=request.params)

    @http.route('/auth_totp/login', type='http', auth='none', methods=['POST'])
    def mfa_login(self, *args, **kwargs):
        token = request.params.get('mfa_login_token')
        try:
            user = request.env['res.users'].user_from_mfa_login_token(token)
        except (MfaTokenInvalidError, MfaTokenExpiredError) as exception:
            if isinstance(exception, MfaTokenInvalidError):
                msg = 'Your MFA login token is not valid. Please try again.'
            if isinstance(exception, MfaTokenExpiredError):
                msg = 'Your MFA login token has expired. Please try again.'

            return http.local_redirect(
                '/web/login',
                query={
                    'redirect': request.params.get('redirect'),
                    'error': msg,
                },
                keep_hash=True,
            )

        confirmation_code = request.params.get('confirmation_code')
        if not user.sudo().validate_mfa_confirmation_code(confirmation_code):
            return http.local_redirect(
                '/auth_totp/login',
                query={
                    'redirect': request.params.get('redirect'),
                    'error': 'Your confirmation code is not correct. Please'
                             ' try again.',
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
        response = Response(http.redirect_with_hash(redirect))

        if request.params.get('remember_device'):
            device_model = request.env['res.users.device']
            device = device_model.sudo().create({'user_id': user.id})
            config_model = request.env['ir.config_parameter'].sudo()
            secret = config_model.get_param('database.secret')
            device_cookie = JsonSecureCookie({'device_id': device.id}, secret)
            cookie_lifetime = timedelta(days=30)
            cookie_exp = datetime.now() + cookie_lifetime
            device_cookie = device_cookie.serialize(cookie_exp)
            cookie_key = 'trusted_devices_%s' % user.id
            cookie_security = config_model.get_param('auth_totp.secure_cookie')
            security_flag = False if cookie_security == '0' else True
            response.set_cookie(
                cookie_key,
                device_cookie,
                max_age=cookie_lifetime.total_seconds(),
                expires=cookie_exp,
                httponly=True,
                secure=security_flag,
            )

        return response
