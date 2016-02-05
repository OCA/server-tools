# -​*- coding: utf-8 -*​-
##############################################################################
#
#    Copyright 2009-2016 Trobz (<http://trobz.com>).
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
import re
import logging

from openerp import models, api
from openerp.exceptions import ValidationError
from openerp.tools.safe_eval import safe_eval
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)
try:
    import cracklib
except ImportError:
    _logger.debug('Cannot import the library cracklib.')
    import crack as cracklib


class ResUsers(models.Model):

    _inherit = "res.users"

    def _set_password(self, cr, uid, user_id, password, context=None):
        """
        Overwrite to call the function to validate the new password
        """
        self.validate_new_password(cr, uid, user_id, password, context)
        return super(ResUsers, self)._set_password(cr, uid, user_id, password,
                                                   context)

    @api.cr_uid_id_context
    def validate_new_password(self, cr, uid, user_id, password, context=None):
        """
        Check constraints for password
           + Long enough
           + Contain at least 1 letter in lower case
           + Contain at least 1 letter in upper case
           + Contain at least 1 number
        Check with function from cracklib
        """
        icp = self.pool['ir.config_parameter']
        length_pw = icp.get_param(cr, uid, 'length_password', 'False')
        length_pw = int(length_pw)

        if len(password) < length_pw:
            raise ValidationError(
                _("Password must have at least %s characters") %
                (length_pw,))
        if not (re.search(r'[A-Z]', password) and
                re.search(r'[a-z]', password) and
                re.search(r'\d', password)):
            raise ValidationError(_("Password must have: \n\
                - at least one letter in lower case \n\
                - at least one letter in upper case \n\
                - at least one number"))

        use_cracklib = icp.get_param(cr, uid, 'password_check_cracklib',
                                     'False')
        if safe_eval(use_cracklib):
            try:
                cracklib.VeryFascistCheck(password)
            except ValueError, error_msg:
                raise ValidationError(_(error_msg))
        return True
