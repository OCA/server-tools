# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Sergio Teruel
# (c) 2015 Antiun Ingeniería S.L. - Carlos Dauden
# © 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.addons.auth_signup.controllers.main import AuthSignupHome
from openerp.http import request


class AuthSignupHome(AuthSignupHome):
    def _signup_with_values(self, token, values):
        account_type = request.params.get('account_type')
        if account_type in {"customer", "supplier"}:
            values.setdefault(account_type, True)
        return super(AuthSignupHome, self)._signup_with_values(token, values)
