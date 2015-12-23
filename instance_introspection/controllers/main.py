# coding: utf-8
# © 2015 Vauxoo - http://www.vauxoo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# info Vauxoo (info@vauxoo.com)
# coded by: nhomar@vauxoo.com
# planned by: nhomar@vauxoo.com

import logging

import openerp
from openerp.addons.web import http
from openerp.http import request

_logger = logging.getLogger(__name__)


class InstanceIntrospection(http.Controller):

    _main_info = {}

    @http.route('/instance_introspection',
                type='http', auth="user")
    def index(self, *args, **post):
        """ Returns some information regarding how instance is configured,
        basically bringing to frontend the information of the instance.
        """
        return request.render('instance_introspection.addons', {
        })

    @http.route('/instance_introspection/main_info',
                type='http', auth="user")
    def main_reload(self, *args, **post):
        """ Just to set global variable
        """
        return request.render('instance_introspection.main_info', {
            'main_info': self._main_info,
        })

    @http.route('/instance_introspection/reload',
                type='http', auth="user")
    def index_reload(self, *args, **post):
        """ Returns the list elements on repositories.
        """
        modules = request.registry['ir.module.module']
        addons_path = openerp.conf.addons_paths
        addons = [
            {'id': addon.replace('/', '_').replace('.', '_'),
             'info': modules.get_info(addon),
             'path': addon}
            for addon in addons_path]
        self._main_info = modules.get_header(addons)
        return request.render('instance_introspection.repository_list', {
            'addons': addons,
        })
