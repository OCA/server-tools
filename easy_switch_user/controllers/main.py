from odoo import http
from odoo.http import request


class SwitchController(http.Controller):
    @http.route('/easy_switch_user/switch', type='json', auth="none", sitemap=False)
    def switch(self, login, password):
        uid = request.session.authenticate(request.db, login, password)
        if uid is False:
            raise Exception('Login Failed')
