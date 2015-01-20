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
from openerp.osv import orm
from openerp.tools.translate import _


class ir_model_fields(orm.Model):
    _inherit = 'ir.model.fields'

    def action_unserialize_field(self, cr, uid, ids, context=None):
        step = 1000
        offset = 0

        # Prevent _auto_init to commit the transaction
        # before the data is migrated safely
        commit_org = cr.commit
        cr.commit = lambda *args: None

        try:
            for this in self.browse(cr, uid, ids, context=context):
                pool_obj = self.pool.get(this.model_id.model)
                self.create_database_column(cr, uid, pool_obj, this.name,
                                            context=context)
                while True:
                    ids = pool_obj.search(
                        cr, uid,
                        [(this.serialization_field_id.name, '!=', '{}')],
                        offset=offset * step, limit=step, context=context)
                    if not ids:
                        break
                    for data in pool_obj.read(
                            cr, uid, ids,
                            [this.serialization_field_id.name],
                            context=context):
                        self.unserialize_field(
                            cr, uid, pool_obj, data,
                            this.serialization_field_id.name,
                            this.name, context=context)
                    offset += 1
        finally:
            cr.commit = commit_org

        return True

    def create_database_column(self, cr, uid, pool_obj, field_name,
                               context=None):
        old = pool_obj._columns[field_name]
        if not old.manual:
            raise orm.except_orm(
                _('Error'),
                _('This operation can only be performed on manual fields'))
        if old._type == 'many2many':
            # Cross table name length of manually created many2many
            # fields can easily become too large. Although it would
            # probably work if the table name length was within bounds,
            # this scenario has not been tested because of this limitation.
            raise orm.except_orm(
                _("Error"),
                _("Many2many fields are not supported. See "
                  "https://bugs.launchpad.net/openobject-server/+bug/1174078 "
                  "for more information"))
        if old._type == 'one2many':
            # How to get a safe field name for the relation field
            # on the target model?
            raise orm.except_orm(
                _("Error"),
                _("One2many fields are not handled yet"))

        # ORM prohibits to change the 'storing system' of the field
        cr.execute("""
            UPDATE ir_model_fields
            SET serialization_field_id = NULL
            WHERE name = %s and model = %s
            """, (field_name, pool_obj._name))

        del pool_obj._columns[field_name]
        pool_obj.__init__(self.pool, cr)
        pool_obj._auto_init(cr, {'update_custom_fields': True})

    def unserialize_field(self, cr, uid, pool_obj, read_record,
                          serialization_field_name, field_name,
                          context=None):
        serialized_values = read_record[serialization_field_name]
        if field_name not in serialized_values:
            return False

        value = serialized_values.pop(field_name)
        if pool_obj._columns[field_name]._type in ('many2many', 'one2many'):
            value = [(6, 0, value)]

        return pool_obj.write(
            cr, uid, read_record['id'],
            {
                field_name: value,
                serialization_field_name: serialized_values,
            },
            context=context)
