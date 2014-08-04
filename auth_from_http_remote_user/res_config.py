# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Laurent Mignon
#    Copyright 2014 'ACSONE SA/NV'
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields
from openerp.tools.safe_eval import safe_eval


class auth_from_http_remote_user_configuration(orm.TransientModel):
    _inherit = 'base.config.settings'

    _columns = {
        'default_login_page_disabled': fields.boolean("Disable login page when "
                                                      "login with HTTP Remote "
                                                      "User",
                                                      help="""
Disable the default login page.
If the HTTP_REMOTE_HEADER field is not found or no user matches the given one,
the system will display a login error page if the login page is disabled.
Otherwise the normal login page will be displayed.
    """),
    }

    def is_default_login_page_disabled(self, cr, uid, fields, context=None):
        vals = self.get_default_default_login_page_disabled(cr,
                                                            uid,
                                                            fields,
                                                            context=context)
        return vals.get('default_login_page_disabled', False)

    def get_default_default_login_page_disabled(self, cr, uid, fields,
                                                context=None):
        icp = self.pool.get('ir.config_parameter')
        # we use safe_eval on the result, since the value of
        # the parameter is a nonempty string
        is_disabled = icp.get_param(cr, uid, 'default_login_page_disabled',
                                    'False')
        return {'default_login_page_disabled': safe_eval(is_disabled)}

    def set_default_default_login_page_disabled(self, cr, uid, ids,
                                                context=None):
        config = self.browse(cr, uid, ids[0], context=context)
        icp = self.pool.get('ir.config_parameter')
        # we store the repr of the value, since the value of the parameter
        # is a required string
        icp.set_param(cr, uid, 'default_login_page_disabled',
                      repr(config.default_login_page_disabled))
