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


class IrModel(orm.Model):

    _inherit = 'ir.model'
    _columns = {
        'validator_line_ids': fields.one2many(
            'ir.model.validator.line', 'name', 'Validators'),
    }

    def check_vals(self, cr, uid, vals, model, context=None):
        for validator_line in model.validator_line_ids:
            if validator_line.field_id.name in vals:
                pattern = re.compile(validator_line.regex_id.regex)
                if not pattern.match(vals[validator_line.field_id.name]):
                    raise orm.except_orm(
                        _('Error'),
                        _('Expression %s not valid for %s') % (
                            validator_line.regex_id.regex,
                            vals[validator_line.field_id.name]))
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
            res = old_write(cr, uid, ids, vals, context=context, **kwargs)
            return res

        return wrapper

    def _register_hook(self, cr, ids=None):
        """ Wrap the methods `create` and `write` of the model
        """
        res = super(IrModel, self)._register_hook(cr)
        if ids is None:
            ids = self.search(
                cr, SUPERUSER_ID, [('validator_line_ids', '!=', False)])
        updated = False
        for model in self.browse(cr, SUPERUSER_ID, ids):
            if model.validator_line_ids:
                model_name = model.model
                model_obj = self.pool.get(model_name)
                if model_obj and not hasattr(
                    model_obj, 'field_validator_checked'
                ):
                    model_obj.create = self._wrap_create(
                        model_obj.create, model)
                    model_obj.write = self._wrap_write(model_obj.write, model)
                    model_obj.field_validator_checked = True
                    updated = True
        if updated:
            openerp.modules.registry.RegistryManager.\
                signal_registry_change(cr.dbname)
        return res

    def create(self, cr, uid, vals, context=None):
        res_id = super(IrModel, self).create(
            cr, uid, vals, context=context)
        self._register_hook(cr, [res_id])
        return res_id

    def write(self, cr, uid, ids, vals, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = super(IrModel, self).write(cr, uid, ids, vals, context=context)
        self._register_hook(cr, ids)
        return res


class IrModelValidatorLine(orm.Model):
    _name = "ir.model.validator.line"
    _columns = {
        'name': fields.many2one('ir.model', string="Model", required=True),
        'field_id': fields.many2one(
            'ir.model.fields', 'Field', required=True),
        'regex_id': fields.many2one(
            'ir.model.fields.regex', string="Validator",
            required=True),
        }
