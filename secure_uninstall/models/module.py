# coding: utf-8
# Copyright 2014 David BEAL @ Akretion <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from openerp.exceptions import Warning as UserError
from openerp.tools.config import config


class BaseModuleUpgrade(models.TransientModel):
    _inherit = 'base.module.upgrade'

    password = fields.Char(
        string='Password', required=True,
        help="'admin_passwd' value from Odoo configuration file "
             "(aka 'Master Password')")

    @api.multi
    def upgrade_module(self):
        config_passwd = config.get("admin_passwd")
        for elm in self:
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
        return super(BaseModuleUpgrade, self).upgrade_module()
