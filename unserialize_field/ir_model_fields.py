# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Therp BV (<http://therp.nl>)
#    All Rights Reserved
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
from openerp.osv.orm import Model
from openerp.osv import fields


class ir_model_fields(Model):
    _inherit = 'ir.model.fields'

    def action_unserialize_field(self, cr, uid, ids, context=None):
        step = 1000
        offset = 0

        for this in self.browse(cr, uid, ids, context=context):
            pool_obj = self.pool.get(this.model_id.model)
            self.create_database_column(cr, uid, pool_obj, this.name)
            while True:
                ids = pool_obj.search(
                        cr, uid, 
                        [(this.serialization_field_id.name, '!=', '{}')],
                        offset=offset*step, limit=step, context=context)
                if not ids:
                    break
                for data in pool_obj.read(cr, uid, ids,
                                          [this.serialization_field_id.name],
                                          context=context):
                    self.unserialize_field(cr, uid, pool_obj, data,
                                           this.serialization_field_id.name,
                                           this.name)
                offset += 1
        return True

    def create_database_column(self, cr, uid, pool_obj, field_name):
        old = pool_obj._columns[field_name]
        field_declaration_args = []
        field_declaration_kwargs = dict(
                manual=False,
                string=old.string,
                required=old.required,
                readonly=old.readonly,
                domain=old._domain,
                context=old._context,
                states=old.states,
                priority=old.priority,
                change_default=old.change_default,
                size=old.size,
                ondelete=old.ondelete,
                translate=old.translate,
                select=old.select,
                )

        if old._type == 'many2one':
            field_declaration_args = [old._obj]
        elif old._type == 'selection':
            field_declaration_args = [old.selection]
        elif old._type == 'one2many':
            field_declaration_args = [old._obj, old._fields_id]
            field_declaration_kwargs['limit'] = old._limit
        elif old._type == 'many2many':
            field_declaration_args = [old._obj]
            field_declaration_kwargs['rel'] = old._rel
            field_declaration_kwargs['id1'] = old._id1
            field_declaration_kwargs['id2'] = old._id2
            field_declaration_kwargs['limit'] = old._limit

        field_declaration = getattr(fields, old._type)(
                *field_declaration_args,
                **field_declaration_kwargs)

        pool_obj._columns[field_name] = field_declaration
        pool_obj._auto_init(cr, {})

    def unserialize_field(self, cr, uid, pool_obj, read_record,
                          serialization_field_name, field_name):
        if not field_name in read_record[serialization_field_name]:
            return False
        pool_obj.write(
                cr, uid, read_record['id'], 
                {
                    field_name:
                        read_record[serialization_field_name][field_name],
                })
