# coding: utf-8
##############################################################################
#
#    Copyright (C) All Rights Reserved 2014 Akretion
#    @author David BEAL <david.beal@akretion.com>
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
###############################################################################

from openerp.osv import orm, fields
from openerp.tools.config import config


class Module(orm.Model):
    _inherit = 'ir.module.module'

    def button_uninstall(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        if 'uninstall_authorized' in context:
            ctx = context.copy()
            del ctx['uninstall_authorized']
            super(Module, self).button_uninstall(
                cr, uid, ids, context=ctx)
            return self._button_immediate_function(
                cr, uid, ids, self.button_uninstall, context=ctx)
        else:
            _, view_id = self.pool['ir.model.data'].get_object_reference(
                cr, uid, 'secure_uninstall', 'view_uninstall_wizard_form')
            return {
                'view_id': view_id,
                'view_mode': 'form',
                'res_model': 'uninstall.check.wizard',
                'context': {'module_id': ids[0]},
                'name': "Uninstall Authorization",
                'type': 'ir.actions.act_window',
                'target': 'new',
            }


class UninstallCheckWizard(orm.TransientModel):
    _name = 'uninstall.check.wizard'

    _columns = {
        'password': fields.char(
            string='Password', required=True,
            help="'admin_passwd' value from Odoo configuration file "
                 "(aka 'Master Password')")
    }

    def check_password(self, cr, uid, ids, context=None):
        for elm in self.browse(cr, uid, ids, context=context):
            config_passwd = config.get("admin_passwd")
            if not config_passwd:
                raise orm.except_orm(
                    'Missing configuration key',
                    "'admin_passwd' configuration key "
                    "(aka 'Master Password') is not set in \n"
                    "your Odoo server configuration file: "
                    "please set it a value")
            if elm.password != config_passwd:
                raise orm.except_orm(
                    "Password Error",
                    "Issue\n_____\nProvided password '%s' doesn't match with "
                    "'Master Password' ('admin_passwd' key) found in the "
                    "Odoo server configuration file ."
                    "\n\nResolution\n__________\n"
                    "Please check your password and retry or cancel"
                    % elm.password)
            context['uninstall_authorized'] = True
            module_id = context.get('module_id')
            self.pool['ir.module.module'].button_uninstall(
                cr, uid, [module_id], context=context)
        return True
