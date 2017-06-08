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
    orm,
    fields)
from openerp.tools.safe_eval import safe_eval
from openerp.tools.translate import _


class BaseConfigSettings(orm.TransientModel):
    _inherit = 'base.config.settings'

    _columns = {
        'auth_password_min_character': fields.integer(
            'Minimum Password Length',
            help="Use the Minimum Password Length to determine how long the \
            password should be. Set 0 if dont want to set any limit"),
        'auth_password_has_capital_letter': fields.boolean(
            'Use capital letters',
            help="check this if you want to enforce the presence of at least \
            one uppercase letter in the password"),
        'auth_password_has_digit': fields.boolean(
            'Use digits',
            help="check this if you want to enforce the presence of at least \
            one digit (0...9) in the password"),
        'auth_password_has_special_letter': fields.boolean(
            'Use Special Characters',
            help="check this if you want to enforce the presence of at least \
            one 'special' character (e.g. #, , $, !, ^, &...) in the password")
    }

    def get_default_auth_password_has_digit(self, cr, uid, fields, ctx=None):
        icp = self.pool['ir.config_parameter']
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
        if config.auth_password_min_character < 5:
            raise orm.except_orm(
                _('Error'),
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
