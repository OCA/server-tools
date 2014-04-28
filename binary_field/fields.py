# -*- coding: utf-8 -*-
###############################################################################
#
#   Module for OpenERP 
#   Copyright (C) 2014 Akretion (http://www.akretion.com).
#   @author Sébastien BEAU <sebastien.beau@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp.osv import fields, orm

class BinaryField(fields.function):

    def __init__(self, string, filters=None, **kwargs):
        self.filters = filters
        super(BinaryField, self).__init__(
            string=string,
            fnct=self._fnct_read,
            fnct_inv=self._fnct_write,
            type='binary',
            multi=False,
            **kwargs)

    def _get_binary_id(self, cr, uid, obj, field_name, record_id, context=None):
        cr.execute(
            "SELECT " + field_name +"_info_id FROM " + obj._table + " WHERE id = %s",
            (record_id,))
        return cr.fetchone()[0]

    def _get_binary(self, cr, uid, obj, field_name, record_id, context=None):
        binary_obj = obj.pool['binary.binary']
        binary_id = self._get_binary_id(
            cr, uid, obj, field_name, record_id, context=context)
        if not binary_id:
            return None
        field_key = "%s-%s" % (obj._name, field_name)
        return binary_obj.get_content(cr, uid, field_key, binary_id, context=context)

    def _fnct_write(self, obj, cr, uid, ids, field_name, value, args,
                    context=None):
        binary_obj = obj.pool['binary.binary']
        if type(ids) in (list, tuple):
            assert len(ids) == 1, 'multi mode is not supported'
            record_id = ids[0]
        else:
            record_id = ids
        field_key = "%s-%s" % (obj._name, field_name)
        binary_id = self._get_binary_id(
            cr, uid, obj, field_name, record_id, context=context)
        if binary_id:
            res_id = binary_obj.update(
                cr, uid, binary_id, value, field_key, context=context)
        else:
            res_id = binary_obj.add(cr, uid, value, field_key, context=context)
            obj.write(cr, uid, record_id, {'%s_info_id' % field_name: res_id}, context=context)
        return True

    def _fnct_read(self, obj, cr, uid, ids, field_name, args, context=None):
        result = {}
        for record_id in ids:
            result[record_id] = self._get_binary(cr, uid, obj, field_name,
                                          record_id, context=context)

#TODO do not forget to add this for compatibility with binary field
#            if val and context.get('bin_size_%s' % name, context.get('bin_size')):
#                res[i] = tools.human_size(long(val))
#            else:
#                res[i] = val
        return result

fields.BinaryField = BinaryField


original__init__ = orm.BaseModel.__init__

def __init__(self, pool, cr):
    original__init__(self, pool, cr)
    if self.pool['binary.binary']:
        print 'I should update something here'
        additionnal_field = {}
        for field in self._columns:
            if isinstance(self._columns[field], BinaryField):
                additionnal_field['%s_info_id'%field] = \
                    fields.many2one('binary.binary', 'Binary')
        self._columns.update(additionnal_field)

orm.BaseModel.__init__ = __init__
