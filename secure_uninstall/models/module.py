# coding: utf-8
# Copyright 2014 David BEAL @ Akretion <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from openerp.exceptions import Warning as UserError
from openerp.tools.config import config


class BaseModuleUpgrade(models.TransientModel):
    _inherit = 'base.module.upgrade'

    password = fields.Char(
        string='Password',
        help="'secure_uninstall' value from Odoo configuration file ")

    @api.multi
    def upgrade_module(self):
        config_passwd = config.get("secure_uninstall")
        for elm in self:
            if not config_passwd:
                raise UserError(
                    "Missing configuration key\n--------------------\n"
                    "'secure_uninstall' configuration key "
                    "is not set in \n"
                    "your Odoo server configuration file: "
                    "please set it a value")
            if elm.password != config_passwd:
                raise UserError(
                    "Password Error\n--------------------\n"
                    "Provided password '%s' doesn't match with "
                    "'Master Password'\n('secure_uninstall' key) found in the "
                    "Odoo server configuration file ."
                    "\n\nResolution\n-------------\n"
                    "Please check your password and retry or cancel"
                    % elm.password)
            # keep this password in db is insecure, then we remove it
            elm.password = False
        return super(BaseModuleUpgrade, self).upgrade_module()
