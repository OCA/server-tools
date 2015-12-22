# coding: utf-8
# © 2015 Vauxoo - http://www.vauxoo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# info Vauxoo (info@vauxoo.com)
# coded by: nhomar@vauxoo.com
# planned by: nhomar@vauxoo.com

import base64
import logging
import werkzeug

from openerp.addons.web import http
from openerp.exceptions import AccessError
from openerp.http import request
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class InstanceIntrospection(http.Controller):
    @http.route('/instance_introspection', type='http', auth="user", website=True)
    def slides_index(self, *args, **post):
        """ Returns some information regarding how instance is configured,
        basically bringing to frontend the information of the instance..
        """
        addons_path = []
        return request.render('instance_introspection.addons', {
            'addons': addons_path
        })