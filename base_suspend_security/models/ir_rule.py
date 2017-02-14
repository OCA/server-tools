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
from openerp import models, api
from ..base_suspend_security import BaseSuspendSecurityUid, SUSPEND_METHOD


class IrRule(models.Model):
    _inherit = 'ir.rule'

    @api.model
    def domain_get(self, model_name, mode='read'):
        if isinstance(self.env.uid, BaseSuspendSecurityUid):
            return [], [], ['"%s"' % self.pool[model_name]._table]
        return super(IrRule, self).domain_get(model_name, mode=mode)

    def _setup_complete(self, cr, uid):
        if not hasattr(models.BaseModel, SUSPEND_METHOD):
            setattr(models.BaseModel, SUSPEND_METHOD,
                    lambda self: self.sudo(
                        user=BaseSuspendSecurityUid(self.env.uid)))
        return super(IrRule, self)._setup_complete(cr, uid)
