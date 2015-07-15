# -*- coding: utf-8 -*-
##############################################################################
#
#    This module copyright (C) 2015 Therp BV (<http://therp.nl>).
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
from openerp import models
from ..base_suspend_security import BaseSuspendSecurityUid


class ResUsers(models.Model):
    _inherit = 'res.users'
    
    @classmethod
    def _browse(cls, env, ids):
        """be sure we browse ints, ids laread is normalized"""
        return super(ResUsers, cls)._browse(
            env,
            [
                i if not isinstance(i, BaseSuspendSecurityUid)
                else super(BaseSuspendSecurityUid, i).__int__()
                for i in ids
            ])
