# coding: utf-8
# Copyright 2014 David BEAL @ Akretion <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import _, models, fields, api
from openerp.exceptions import Warning as UserError
from openerp.tools.config import config


def _get_authorized_password():
    """ You can define your own authorized keys
    """
    return [config.get("secure_uninstall"), config.get("admin_passwd")]


class BaseModuleUpgrade(models.TransientModel):
    _inherit = 'base.module.upgrade'

    uninstall_password = fields.Char(
        string='Password',
        help="'secure_uninstall' value from Odoo configuration file ")

    @api.multi
    def upgrade_module(self):
        for elm in self:
            if not config.get("secure_uninstall"):
                self.rollback_state_modules()
                raise UserError(_(
                    "Missing configuration key\n--------------------\n"
                    "'secure_uninstall' configuration key "
                    "is not set in \n"
                    "your Odoo server configuration file: "
                    "please set it a value"))
            if elm.uninstall_password not in _get_authorized_password():
                self.rollback_state_modules()
                raise UserError(_(
                    "Password Error\n--------------------\n"
                    "Provided password '%s' doesn't match with "
                    "'Master Password'\n('secure_uninstall' key) found in "
                    "the Odoo server configuration file ."
                    "\n\nResolution\n-------------\n"
                    "Please check your password and retry or cancel")
                    % elm.uninstall_password)
            # keep this password in db is insecure, then we remove it
            elm.uninstall_password = False
        return super(BaseModuleUpgrade, self).upgrade_module()

    def rollback_state_modules(self):
        modules = self.env['ir.module.module'].browse(
            self._context.get('active_ids'))
        if modules:
            module_ids = modules.downstream_dependencies(
                exclude_states=['uninstalled', 'uninstallable'])
            module_ids = module_ids + list(modules._ids)
            self.env['ir.module.module'].browse(
                module_ids).button_uninstall_cancel()
            self._cr.commit()
        return True
