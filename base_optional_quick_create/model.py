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

from openerp.osv import orm

class ir_model(orm.Model):

    _inherit = 'ir.model'

    def _wrap_name_create(self, old_create, model):
        
        def wrapper(cr, uid, name, context=None):
            import pdb; pdb.set_trace()
            return old_create(cr, uid, name, context=context)

        return wrapper

    def _register_hook(self, cr, ids=None):
        model = 'res.partner'
        model_obj = self.pool.get(model)
        if not hasattr(model_obj, 'check_quick_create'):
            model_obj.name_create = self._wrap_name_create(model_obj.name_create, model)
            model_obj.check_quick_create = True
        return True

    def name_create(self, cr, uid, name, context=None):
        res = super(ir_model, self).name_create(cr, uid, name, context=context)
        self._register_hook(cr, [res])
        return res
