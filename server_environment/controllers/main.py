# coding: utf-8
# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from werkzeug.utils import redirect
from urlparse import urljoin

from openerp.tools.config import config
from openerp import http
from openerp.http import request, Controller


class ServerEnvironmentController(Controller):

    @http.route(
        '/server_environment_<module_extension>'
        '/static/RUNNING_ENV/<local_path>',
        type='http', auth='public')
    def environment_redirect(self, module_extension, local_path, **kw):
        # Note: module_extension is present to make working
        # the module in normal configuration, with the folder
        # server_environment_files and in demo configuration, with the
        # module  server_environment_files_sample
        running_env = config.get('running_env', "default")
        IrConfigParameter = request.env['ir.config_parameter']
        base_url = IrConfigParameter.get_param('web.base.url', '')
        new_path = "/server_environment_%s/static/%s/%s" % (
            module_extension, running_env, local_path)
        url = urljoin(base_url, new_path)
        return redirect(url, 303)
