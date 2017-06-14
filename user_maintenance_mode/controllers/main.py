# -*- coding: utf-8 -*-

from openerp import http
from openerp.http import request
from openerp.tools.translate import _
import openerp.addons.web.controllers.main as main


class Home(main.Home):

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        res = super(Home, self).web_login(redirect, **kw)
        values = request.params.copy()
        if request.httprequest.method == 'POST':
            uid = request.uid
            if uid is not False:
                maintenance_mode = \
                    request.env.user.browse(uid).maintenance_mode
                if maintenance_mode:
                    values['error'] = _("This user is in maintenance mode")
                    if request.env.ref('web.login', False):
                        return request.render('web.login', values)
        return res
