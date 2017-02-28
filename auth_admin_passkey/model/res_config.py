# -*- encoding: utf-8 -*-
##############################################################################
#
#    Admin Passkey module for Odoo
#    Copyright (C) 2013-2014 GRAP (http://www.grap.coop)
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
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

from openerp.osv import fields
from openerp.osv.orm import TransientModel
from openerp.tools.safe_eval import safe_eval


class base_config_settings(TransientModel):
    _inherit = 'base.config.settings'

    # Getter / Setter Section
    def get_default_auth_admin_passkey_send_to_admin(
            self, cr, uid, ids, context=None):
        icp = self.pool['ir.config_parameter']
        return {
            'auth_admin_passkey_send_to_admin': safe_eval(icp.get_param(
                cr, uid, 'auth_admin_passkey.send_to_admin', 'True')),
        }

    def set_auth_admin_passkey_send_to_admin(self, cr, uid, ids, context=None):
        config = self.browse(cr, uid, ids[0], context=context)
        icp = self.pool['ir.config_parameter']
        icp.set_param(
            cr, uid, 'auth_admin_passkey.send_to_admin',
            repr(config.auth_admin_passkey_send_to_admin))

    def get_default_auth_admin_passkey_send_to_user(
            self, cr, uid, ids, context=None):
        icp = self.pool['ir.config_parameter']
        return {
            'auth_admin_passkey_send_to_user': safe_eval(icp.get_param(
                cr, uid, 'auth_admin_passkey.send_to_user', 'True')),
        }

    def set_auth_admin_passkey_send_to_user(self, cr, uid, ids, context=None):
        config = self.browse(cr, uid, ids[0], context=context)
        icp = self.pool['ir.config_parameter']
        icp.set_param(
            cr, uid, 'auth_admin_passkey.send_to_user',
            repr(config.auth_admin_passkey_send_to_user))

    # Columns Section
    _columns = {
        'auth_admin_passkey_send_to_admin': fields.boolean(
            'Send email to admin user.',
            help="""When the administrator use his password to login in """
            """with a different account, Odoo will send an email """
            """to the admin user.""",
        ),
        'auth_admin_passkey_send_to_user': fields.boolean(
            string='Send email to user.',
            help="""When the administrator use his password to login in """
            """with a different account, Odoo will send an email """
            """to the account user.""",
        ),
    }
