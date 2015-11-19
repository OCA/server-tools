# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Sergio Teruel
# (c) 2015 Antiun Ingeniería S.L. - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.addons.auth_signup.controllers.main import AuthSignupHome
from openerp.http import request


class AuthSignupHome(AuthSignupHome):

    def _signup_with_values(self, token, values):
        qcontext = request.params.copy()
        values.update(account_type=qcontext.get('account_type', False))
        return super(AuthSignupHome, self)._signup_with_values(token, values)
