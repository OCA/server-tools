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
from openerp import models, tools
from ..base_suspend_security import BaseSuspendSecurityUid


class IrModelAccess(models.Model):
    _inherit = 'ir.model.access'

    @tools.ormcache_context('uid', 'model', 'mode', 'raise_exception',
                            keys=('lang',))
    def check(self, cr, uid, model, mode='read', raise_exception=True,
              context=None):
        # pylint: disable=old-api7-method-defined
        if isinstance(uid, BaseSuspendSecurityUid):
            return True
        return super(IrModelAccess, self).check(
            cr, uid, model, mode=mode, raise_exception=raise_exception,
            context=context)
