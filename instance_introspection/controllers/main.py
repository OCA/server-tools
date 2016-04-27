# coding: utf-8
# © 2015 Vauxoo - http://www.vauxoo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# info Vauxoo (info@vauxoo.com)
# coded by: nhomar@vauxoo.com
# planned by: nhomar@vauxoo.com

import logging
import simplejson

import openerp
from openerp.addons.web import http
from openerp.http import request

_logger = logging.getLogger(__name__)


class InstanceIntrospection(http.Controller):

    _main_info = {}
    _addons = []

    @http.route('/instance_introspection', type='http', auth="user")
    def index(self, *args, **post):
        """Returns some information regarding how instance is configured,
        basically bringing to frontend the information of the instance.
        """
        return request.render('instance_introspection.addons', {})

    @http.route('/instance_introspection/main_info',
                type='http', auth="user")
    def main_reload(self, *args, **post):
        """Just to set global variable indicators
        """
        modules = request.registry['ir.module.module']
        self._main_info = modules.get_header(self._addons)
        return request.render('instance_introspection.main_info', {
            'main_info': self._main_info,
        })

    @http.route('/instance_introspection/pyenv',
                type='http', auth="user")
    def index_pyenv(self, *args, **post):
        return request.render('instance_introspection.pyinfo', {
            'info_html': request.registry['ir.module.module'].get_pyinfo(),
        })

    def get_branch_info(self, module=None):
        """Returns the info of a specific module or
        the all modules defined in the addons_path
        @param module: string with the name of module that you want
                       to get its info
        """
        modules = request.registry['ir.module.module']
        addons_path = module and (module, ) or openerp.conf.addons_paths
        addons = [
            {'id': addon.replace('/', '_').replace('.', '_'),
             'info': modules.get_info(addon),
             'path': addon}
            for addon in addons_path]
        return addons

    @http.route('/instance_introspection/reload',
                type='http', auth="user")
    def index_reload(self, *args, **post):
        """Returns the list elements on repositories.
        """
        addons = self.get_branch_info()
        self._addons = addons
        return request.render('instance_introspection.repository_list', {
            'addons': addons,
        })

    @http.route('/instance_introspection.json',
                type='http', auth='none')
    def get_json_info(self, *args, **post):
        """Returns json with the list elements on repositories.
        """
        addons = self.get_branch_info()
        return simplejson.dumps(addons)
