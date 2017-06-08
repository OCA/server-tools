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
import types


class auth_from_http_remote_user_configuration(orm.TransientModel):
    _name = 'auth_from_http_remote_user.config.settings'
    _inherit = 'res.config.settings'

    _columns = {
        'default_login_page_disabled': fields.boolean("Disable login page",
                                                      help="""
Disable the default login page.
If the HTTP_REMOTE_HEADER field is not found or no user matches the given one,
the system will display a login error page if the login page is disabled.
Otherwise the normal login page will be displayed.
    """),
    }

    def is_default_login_page_disabled(self, cr, uid, fields, context=None):
        ir_config_obj = self.pool['ir.config_parameter']
        default_login_page_disabled = ir_config_obj.get_param(cr,
                                                              uid,
                                                              'auth_from_http_remote_user.default_login_page_disabled')
        if isinstance(default_login_page_disabled, types.BooleanType):
            return default_login_page_disabled
        return safe_eval(default_login_page_disabled)

    def get_default_default_login_page_disabled(self, cr, uid, fields, context=None):
        default_login_page_disabled = self.is_default_login_page_disabled(cr, uid, fields, context)
        return {'default_login_page_disabled': default_login_page_disabled}

    def set_default_default_login_page_disabled(self, cr, uid, ids, context=None):
        config = self.browse(cr, uid, ids[0], context)
        ir_config_parameter_obj = self.pool['ir.config_parameter']
        ir_config_parameter_obj.set_param(cr,
                                          uid,
                                          'auth_from_http_remote_user.default_login_page_disabled',
                                          repr(config.default_login_page_disabled))
