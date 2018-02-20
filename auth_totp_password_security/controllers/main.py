# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

from odoo.http import redirect_with_hash, request, route
from odoo.addons.auth_totp.controllers.main import AuthTotp


class AuthTotpPasswordSecurity(AuthTotp):
    @route()
    def mfa_login_post(self, *args, **kwargs):
        """Overload to check password expiration after MFA login"""
        super_object = super(AuthTotpPasswordSecurity, self)
        response = super_object.mfa_login_post(*args, **kwargs)

        if not request.params.get('login_success'):
            return response

        user = request.env['res.users'].sudo().browse(request.uid)
        if user._password_has_expired():
            user.action_expire_password()
            request.session.logout(keep_db=True)
            request.params['login_success'] = False
            return redirect_with_hash(user.partner_id.signup_url)

        return response
