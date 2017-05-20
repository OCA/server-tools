# -*- encoding: utf-8 -*-
##############################################################################
#
#    Authentification - Generate Password module for Odoo
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

# This line is noqa flaged, to allow users to use string functions written
# in ir_config_parameter
import string # flake8: noqa
import random

from openerp.osv.orm import Model, except_orm
from openerp.tools.translate import _
from openerp.tools.safe_eval import safe_eval


class res_users(Model):
    _inherit = 'res.users'

    def generate_password(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        mm_obj = self.pool['mail.mail']
        icp_obj = self.pool['ir.config_parameter']
        imd_obj = self.pool['ir.model.data']
        et_obj = self.pool['email.template']
        globals_dict = {'string': string}
        try:
            int(icp_obj.get_param(
                cr, uid, 'auth_generate_password.password_size'))
        except:
            raise except_orm(_("error"), _("Only digit chars authorized"))
        password_size = safe_eval(
            icp_obj.get_param(
                cr, uid, 'auth_generate_password.password_size'),
            globals_dict=globals_dict
        )
        password_chars = safe_eval(
            icp_obj.get_param(
                cr, uid, 'auth_generate_password.password_chars'),
            globals_dict=globals_dict
        )
        et = imd_obj.get_object(
            cr, uid, 'auth_generate_password', 'generate_password_template')

        for ru in self.browse(cr, uid, ids, context=context):
            if not ru.email:
                raise except_orm(
                    _("Cannot send email: user has no email address."),
                    user.name)
            # Generate Password
            password = "".join([random.choice(
                password_chars) for n in xrange(password_size)])
            self._set_new_password(
                cr, uid, ru.id, None, password, None, context=None)
            # Send Mail
            context['generated_password'] = password
            mail_id = et_obj.send_mail(
                cr, uid, et.id, ru.id, True, context=context)
            del context['generated_password']
        return {}
