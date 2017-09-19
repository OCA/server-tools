# -*- coding: utf-8 -*-
# Copyright 2015 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import operator

from openerp import http
from openerp.http import request
from openerp.addons.auth_signup.controllers.main import AuthSignupHome
from openerp.addons.web.controllers.main import ensure_db, Session

from ..exceptions import PassError


class PasswordSecuritySession(Session):

    @http.route()
    def change_password(self, fields):
        new_password = operator.itemgetter('new_password')(
            dict(map(operator.itemgetter('name', 'value'), fields))
        )
        user_id = request.env.user
        user_id.check_password(new_password)
        return super(PasswordSecuritySession, self).change_password(fields)


class PasswordSecurityHome(AuthSignupHome):

    def do_signup(self, qcontext):
        password = qcontext.get('password')
        user_id = request.env.user
        user_id.check_password(password)
        return super(PasswordSecurityHome, self).do_signup(qcontext)

    @http.route()
    def web_login(self, *args, **kw):
        ensure_db()
        response = super(PasswordSecurityHome, self).web_login(*args, **kw)
        login_success = request.params.get('login_success', True)
        if not request.httprequest.method == 'POST' or not login_success:
            return response
        uid = request.session.authenticate(
            request.session.db,
            request.params['login'],
            request.params['password']
        )
        if not uid:
            return response
        users_obj = request.env['res.users'].sudo()
        user_id = users_obj.browse(request.uid)
        if not user_id._password_has_expired():
            return response
        user_id.action_expire_password()
        redirect = user_id.partner_id.signup_url
        return http.redirect_with_hash(redirect)

    @http.route()
    def web_auth_signup(self, *args, **kw):
        try:
            return super(PasswordSecurityHome, self).web_auth_signup(
                *args, **kw
            )
        except PassError as e:
            qcontext = self.get_auth_signup_qcontext()
            qcontext['error'] = e.message
            return request.render('auth_signup.signup', qcontext)

    @http.route()
    def web_auth_reset_password(self, *args, **kw):
        """ It provides hook to disallow front-facing resets inside of min
        Unfortuantely had to reimplement some core logic here because of
        nested logic in parent
        """
        qcontext = self.get_auth_signup_qcontext()
        if (
            request.httprequest.method == 'POST' and
            qcontext.get('login') and
            'error' not in qcontext and
            'token' not in qcontext
        ):
            login = qcontext.get('login')
            user_ids = request.env.sudo().search(
                [('login', '=', login)],
                limit=1,
            )
            if not user_ids:
                user_ids = request.env.sudo().search(
                    [('email', '=', login)],
                    limit=1,
                )
            user_ids._validate_pass_reset()
        return super(PasswordSecurityHome, self).web_auth_reset_password(
            *args, **kw
        )
