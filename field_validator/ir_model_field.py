# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Agile Business Group sagl (<http://www.agilebg.com>)
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
import re
from openerp.tools.translate import _
import openerp
from openerp import SUPERUSER_ID


class IrModelField(orm.Model):

    _inherit = 'ir.model.field'
    _columns = {
        'regex_validator': fields.char(
            'Validator', size=256,
            help="Regular expression used to validate the field. For example, "
                 "you can add the expression\n%s\nto the email field"
            % r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}\b'),
        }

    def check_vals(self, cr, uid, vals, model, context=None):
        field_ids = self.search(cr, uid, [
            ('model', '=', model), ('regex_validator', '!=', False)
            ], context=context)
        for field in self.browse(cr, uid, field_ids, context=context):
            if field.name in vals:
                p = re.compile(field.regex_validator)
                if not p.match(vals[field.name]):
                    raise orm.except_orm(
                        _('Error'),
                        _('Expression %s not passed for %s') % (
                            field.regex_validator, vals[field.name]))
        return True

    def _wrap_create(self, old_create, model):
        def wrapper(cr, uid, vals, context=None, **kwargs):
            self.check_vals(cr, uid, vals, model, context=context)
            new_id = old_create(cr, uid, vals, context=context, **kwargs)
            return new_id

        return wrapper

    def _wrap_write(self, old_write, model):
        def wrapper(cr, uid, ids, vals, context=None, **kwargs):
            self.check_vals(cr, uid, vals, model, context=context)
            old_write(cr, uid, ids, vals, context=context, **kwargs)
            return True

        return wrapper

    def _register_hook(self, cr, ids=None):
        """ Wrap the methods `create` and `write` of the model
        """
        updated = False
        for field in self.browse(cr, SUPERUSER_ID, ids):
            model = field.model_id.model
            model_obj = self.pool.get(model)
            if not hasattr(model_obj, 'field_validator_checked'):
                model_obj.create = self._wrap_create(
                    model_obj.create, model)
                model_obj.write = self._wrap_write(model_obj.write, model)
                model_obj.field_validator_checked = True
                updated = True
        return updated

    def create(self, cr, uid, vals, context=None):
        res_id = super(IrModelField, self).create(
            cr, uid, vals, context=context)
        if vals.get('regex_validator'):
            if self._register_hook(cr, [res_id]):
                openerp.modules.registry.RegistryManager.\
                    signal_registry_change(cr.dbname)
        return res_id

    def write(self, cr, uid, ids, vals, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        super(IrModelField, self).write(cr, uid, ids, vals, context=context)
        if vals.get('regex_validator'):
            if self._register_hook(cr, ids):
                openerp.modules.registry.RegistryManager.\
                    signal_registry_change(cr.dbname)
        return True
