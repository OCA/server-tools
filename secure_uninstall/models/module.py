# coding: utf-8
# Copyright 2014 David BEAL @ Akretion <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import orm
from openerp import models, fields, api
from openerp.exceptions import Warning as UserError
from openerp.tools.config import config


class Module(orm.Model):
    _inherit = 'ir.module.module'

    def button_uninstall(self, cr, uid, ids, context=None):
        # can't be convert in new api because use button_uninstall fct
        # in _button_immediate_function() is buggy in new api.
        # Next v10 will solve it.
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


class UninstallCheckWizard(models.TransientModel):
    _name = 'uninstall.check.wizard'

    password = fields.Char(
        string='Password', required=True,
        help="'admin_passwd' value from Odoo configuration file "
             "(aka 'Master Password')")

    @api.multi
    def check_password(self):
        for elm in self:
            config_passwd = config.get("admin_passwd")
            if not config_passwd:
                raise UserError(
                    "Missing configuration key\n--------------------\n"
                    "'admin_passwd' configuration key "
                    "(aka 'Master Password') is not set in \n"
                    "your Odoo server configuration file: "
                    "please set it a value")
            if elm.password != config_passwd:
                raise UserError(
                    "Password Error\n--------------------\n"
                    "Provided password '%s' doesn't match with "
                    "'Master Password'\n('admin_passwd' key) found in the "
                    "Odoo server configuration file ."
                    "\n\nResolution\n-------------\n"
                    "Please check your password and retry or cancel"
                    % elm.password)
            module_id = self._context.get('module_id')
            module = self.env['ir.module.module'].browse(module_id)
            module.with_context(uninstall_authorized=True).button_uninstall()
        return True
