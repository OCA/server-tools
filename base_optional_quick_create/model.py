# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Agile Business Group sagl (<http://www.agilebg.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from openerp.osv import orm, fields
from openerp import SUPERUSER_ID
from openerp.tools.translate import _


class IrModel(orm.Model):
    _inherit = 'ir.model'

    _columns = {
        'avoid_quick_create': fields.boolean('Avoid quick create'),
        }

    def _patch_quick_create(self, cr, ids):

        def _wrap_name_create():
            def wrapper(self, cr, uid, name, context=None):
                raise orm.except_orm(
                    _('Error'),
                    _("Can't create quickly. Opening create form"))
            return wrapper

        for model in self.browse(cr, SUPERUSER_ID, ids):
            if model.avoid_quick_create:
                model_name = model.model
                model_obj = self.pool.get(model_name)
                if model_obj and not hasattr(model_obj, 'check_quick_create'):
                    model_obj._patch_method('name_create', _wrap_name_create())
                    model_obj.check_quick_create = True
        return True

    def _register_hook(self, cr):
        self._patch_quick_create(cr, self.search(cr, SUPERUSER_ID, []))
        return super(IrModel, self)._register_hook(cr)

    def create(self, cr, uid, vals, context=None):
        res_id = super(IrModel, self).create(cr, uid, vals, context=context)
        self._patch_quick_create(cr, [res_id])
        return res_id

    def write(self, cr, uid, ids, vals, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = super(IrModel, self).write(cr, uid, ids, vals, context=context)
        self._patch_quick_create(cr, ids)
        return res
