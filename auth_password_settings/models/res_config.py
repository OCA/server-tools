# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Dhaval Patel
#    Copyright (C) 2011 - TODAY Denero Team. (<http://www.deneroteam.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import (
    osv,
    fields)
from openerp.tools.safe_eval import safe_eval
from openerp.tools.translate import _


class BaseConfigSettings(osv.osv_memory):
    _inherit = 'base.config.settings'

    _columns = {
        'auth_password_min_character': fields.integer(
            'Minimum Password Length',
            help="Use the Minimum Password Length to determine how long the \
            password should be. Set 0 if dont want to set any limit"),
        'auth_password_has_capital_letter': fields.boolean(
            'Use capital letters',
            help="Use capital letters to determine the Capital letter that\
            must be used in the password "),
        'auth_password_has_digit': fields.boolean(
            'Use digits',
            help="Use digits to determine the digit(numaric letter)\
            that must be used in the password "),
        'auth_password_has_special_letter': fields.boolean(
            'Use Special Characters',
            help="Use special letters to determine the special letter (e.g. #,\
            $,!,^, &) that must be used in the password"),
    }

    def get_default_auth_password_has_digit(self, cr, uid, fields, ctx=None):
        icp = self.pool.get('ir.config_parameter')
        return {
            'auth_password_min_character': safe_eval(
                icp.get_param(
                    cr,
                    uid,
                    'auth_password_settings.auth_password_min_character',
                    '6'
                )),
            'auth_password_has_capital_letter': safe_eval(
                icp.get_param(
                    cr,
                    uid,
                    'auth_password_settings.auth_password_has_capital_letter',
                    'False'
                )),
            'auth_password_has_digit': safe_eval(
                icp.get_param(
                    cr,
                    uid,
                    'auth_password_settings.auth_password_has_digit',
                    'False'
                )),
            'auth_password_has_special_letter': safe_eval(
                icp.get_param(
                    cr,
                    uid,
                    'auth_password_settings.auth_password_has_special_letter',
                    'False'
                )),
        }

    def set_auth_password_has_digit(self, cr, uid, ids, context=None):
        config = self.browse(cr, uid, ids[0], context=context)
        if (config.auth_password_min_character < 5):
            raise osv.except_osv(
                _('Error!'),
                _('Password Length should not be less then 5.')
            )
        icp = self.pool.get('ir.config_parameter')
        icp.set_param(
            cr,
            uid,
            'auth_password_settings.auth_password_min_character',
            repr(config.auth_password_min_character))
        icp.set_param(
            cr,
            uid,
            'auth_password_settings.auth_password_has_capital_letter',
            repr(config.auth_password_has_capital_letter))
        icp.set_param(
            cr,
            uid,
            'auth_password_settings.auth_password_has_digit',
            repr(config.auth_password_has_digit))
        icp.set_param(
            cr,
            uid,
            'auth_password_settings.auth_password_has_special_letter',
            repr(config.auth_password_has_special_letter))
