# -*- coding: utf-8 -*-
# © Denero Team. (<http://www.deneroteam.com>)
# © 2016 Hans Henrik Gabelgaard www.steingabelgaard.dk
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models, fields, api
from openerp.tools.safe_eval import safe_eval


class BaseConfigSettings(models.TransientModel):
    _inherit = 'base.config.settings'

    auth_password_min_character = fields.Integer(
        'Minimum Password Length',
        help="Use the Minimum Password Length to determine how long the \
        password should be. Set 0 if dont want to set any limit")
    auth_password_has_capital_letter = fields.Boolean(
        'Use capital letters',
        help="Use capital letters to determine the Capital letter that\
        must be used in the password ")
    auth_password_has_digit = fields.Boolean(
        'Use digits',
        help="Use digits to determine the digit(numaric letter)\
        that must be used in the password ")
    auth_password_has_special_letter = fields.Boolean(
        'Use Special Characters',
        help="Use special letters to determine the special letter (e.g. #,\
        $,!,^, &) that must be used in the password")

    @api.multi
    def get_default_auth_password_settings(self, fields=None):
        icp = self.env['ir.config_parameter']
        return {
            'auth_password_min_character': safe_eval(
                icp.get_param(
                    'auth_password_settings.auth_password_min_character',
                    '0'
                )),
            'auth_password_has_capital_letter': safe_eval(
                icp.get_param(
                    'auth_password_settings.auth_password_has_capital_letter',
                    'False'
                )),
            'auth_password_has_digit': safe_eval(
                icp.get_param(
                    'auth_password_settings.auth_password_has_digit',
                    'False'
                )),
            'auth_password_has_special_letter': safe_eval(
                icp.get_param(
                    'auth_password_settings.auth_password_has_special_letter',
                    'False'
                )),
        }

    @api.multi
    def set_auth_password_settings(self):
        self.ensure_one()
        icp = self.env['ir.config_parameter']
        icp.set_param(
            'auth_password_settings.auth_password_min_character',
            repr(self.auth_password_min_character))
        icp.set_param(
            'auth_password_settings.auth_password_has_capital_letter',
            repr(self.auth_password_has_capital_letter))
        icp.set_param(
            'auth_password_settings.auth_password_has_digit',
            repr(self.auth_password_has_digit))
        icp.set_param(
            'auth_password_settings.auth_password_has_special_letter',
            repr(self.auth_password_has_special_letter))
