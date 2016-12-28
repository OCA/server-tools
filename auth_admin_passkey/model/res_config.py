# -*- coding: utf-8 -*-
# Copyright 2013-2014 GRAP (http://www.grap.coop)
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# Copyright 2016 Serpent Consulting Services Pvt. Ltd. 
#                 (http://www.serpentcs.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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
            """with a different account, ODOO will send an email """
            """to the admin user.""",
        ),
        'auth_admin_passkey_send_to_user': fields.boolean(
            string='Send email to user.',
            help="""When the administrator use his password to login in """
            """with a different account, ODOO will send an email """
            """to the account user.""",
        ),
    }
