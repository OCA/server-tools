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
from openerp.tools import image_resize_image
from openerp.tools.translate import _
import os
import logging

_logger = logging.getLogger(__name__)


class Storage(object):

    def __init__(self, cr, uid, obj, field_name):
        self.cr = cr
        self.uid = uid
        self.pool = obj.pool
        self.field_key = ("%s-%s" % (obj._name, field_name)).replace('.', '')
        base_location = self.pool.get('ir.config_parameter').\
            get_param(cr, uid, 'binary.location')
        if not base_location:
            raise orm.except_orm(
                _('Configuration Error'),
                _('The "binary.location" is empty, please fill it in'
                  'Configuration > Parameters > System Parameters'))
        self.base_location = base_location
        self.location = (self.base_location, self.field_key)

    def add(self, value):
        if not value:
            return {}
        file_size = len(value.decode('base64'))
        binary_uid = self.pool['ir.attachment'].\
            _file_write(self.cr, self.uid, self.location, value)
        _logger.debug('Add binary %s/%s' % (self.field_key, binary_uid))
        return {
            'binary_uid': binary_uid,
            'file_size': file_size,
            }

    def update(self, binary_uid, value):
        _logger.debug('Delete binary %s/%s' % (self.field_key, binary_uid))
        self.pool['ir.attachment'].\
            _file_delete(self.cr, self.uid, self.location, binary_uid)
        if not value:
            return {}
        return self.add(value)

    def get(self, binary_uid):
        return self.pool['ir.attachment'].\
            _file_read(self.cr, self.uid, self.location, binary_uid)


class BinaryField(fields.function):

    def __init__(self, string, filters=None, **kwargs):
        new_kwargs = {
            'type': 'binary',
            'string': string,
            'fnct': self._fnct_read,
            'fnct_inv': self._fnct_write,
            'multi': False,
            }
        new_kwargs.update(kwargs)
        self.filters = filters
        super(BinaryField, self).__init__(**new_kwargs)

    def _prepare_binary_meta(self, cr, uid, field_name, res, context=None):
        return {
            '%s_uid' % field_name: res.get('binary_uid'),
            '%s_file_size' % field_name: res.get('file_size'),
            }

    def _fnct_write(self, obj, cr, uid, ids, field_name, value, args,
                    context=None):
        storage = Storage(cr, uid, obj, field_name)
        if not isinstance(ids, (list, tuple)):
            ids = [ids]
        for record in obj.browse(cr, uid, ids, context=context):
            binary_uid = record['%s_uid' % field_name]
            if binary_uid:
                res = storage.update(binary_uid, value)
            else:
                res = storage.add(value)
            vals = self._prepare_binary_meta(cr, uid, field_name, res, context=context)
            record.write(vals)
        return True

    def _fnct_read(self, obj, cr, uid, ids, field_name, args, context=None):
        result = {}
        storage = Storage(cr, uid, obj, field_name)
        for record in obj.browse(cr, uid, ids, context=context):
            binary_uid = record['%s_uid' % field_name]
            if binary_uid:
                result[record.id] = storage.get(binary_uid)
            else:
                result[record.id] = None


#TODO do not forget to add this for compatibility with binary field
#            if val and context.get('bin_size_%s' % name, context.get('bin_size')):
#                res[i] = tools.human_size(long(val))
#            else:
#                res[i] = val
        return result


class ImageField(BinaryField):

    def __init__(self, string, filters=None, **kwargs):
        self.filters = filters
        super(ImageField, self).__init__(
            string=string,
            **kwargs)

    def _fnct_write(self, obj, cr, uid, ids, field_name, value, args,
                    context=None):
        super(ImageField, self)._fnct_write(
            obj, cr, uid, ids, field_name, value, args, context=context)
        for name, field in obj._columns.items():
            if isinstance(field, ImageResizeField) \
                    and field.related_field == field_name:
                field._refresh_cache(
                    obj, cr, uid, ids, name, context=context)
        return True


class ImageResizeField(ImageField):

    def __init__(self, string, related_field, height, width,
                 filters=None, **kwargs):
        self.filters = filters
        self.height = height
        self.width = width
        self.related_field = related_field
        super(ImageResizeField, self).__init__(
            string=string,
            **kwargs)

    def _get_binary(self, cr, uid, obj, field_name, record_id, context=None):
        #Idée via le fonction store, je trigger le write
        #et la en fonciton du mode soit simplement je vire les images
        #soit je les vire et je les regénère
        if context.get('bin_size'):
            return 2
        return super(ImageResizeField, self)._get_binary(
            cr, uid, obj, field_name, record_id, context=context)

    def _refresh_cache(self, obj, cr, uid, ids, field_name, context=None):
        if not isinstance(ids, (list, tuple)):
            ids = [ids]
        for record_id in ids:
            _logger.debug('Refresh Image Cache from the field %s of object %s '
                          'id : %s' % (field_name, obj._name, record_id))
            field = obj._columns[field_name]
            record = obj.browse(cr, uid, record_id, context=context)
            original_image = record[field.related_field]
            if original_image:
                size = (field.height, field.width)
                resized_image = image_resize_image(original_image, size)
            else:
                resized_image = None
            ctx = context.copy()
            ctx['refresh_image_cache'] = True
            self._fnct_write(obj, cr, uid, [record_id], field_name,
                             resized_image, None, context=ctx)

    def _fnct_write(self, obj, cr, uid, ids, field_name, value, args,
                    context=None):
        if context is not None and context.get('refresh_image_cache'):
            field = field_name
        else:
            field = obj._columns[field_name].related_field
        return super(ImageResizeField, self)._fnct_write(
            obj, cr, uid, ids, field, value, args, context=context)


fields.BinaryField = BinaryField
fields.ImageField = ImageField
fields.ImageResizeField = ImageResizeField


original__init__ = orm.BaseModel.__init__


def __init__(self, pool, cr):
    original__init__(self, pool, cr)
    if self.pool.get('binary.field.installed'):
        additionnal_field = {}
        for field in self._columns:
            if isinstance(self._columns[field], BinaryField):
                additionnal_field.update({
                    '%s_uid' % field:
                        fields.char('%s UID' % self._columns[field].string),
                    '%s_file_size' % field:
                        fields.char('%s File Size' % self._columns[field].string),
                    })

            #Inject the store invalidation function for ImageResize
            if isinstance(self._columns[field], ImageResizeField):
                self._columns[field].store = {
                    self._name: (
                        lambda self, cr, uid, ids, c={}: ids,
                        [self._columns[field].related_field],
                        10),
                }
        self._columns.update(additionnal_field)


orm.BaseModel.__init__ = __init__


class IrAttachment(orm.Model):
    _inherit = 'ir.attachment'

    def _full_path(self, cr, uid, location, path):
        #TODO add the posibility to customise the field_key
        #maybe we can add a the field key in the ir.config.parameter
        #and then retrieve an new path base on the config?

        # Hack for passing the field_key in the full path
        if isinstance(location, tuple):
            base_location, field_key = location
            path = os.path.join(field_key, path)
        else:
            base_location = location
        return super(IrAttachment, self).\
            _full_path(cr, uid, base_location, path)


class BinaryFieldInstalled(orm.AbstractModel):
    _name = 'binary.field.installed'
