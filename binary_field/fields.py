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

import hashlib
from openerp.osv import fields, orm
from openerp.tools import image_resize_image
from openerp.tools.translate import _
from openerp import tools
import os
import sys
import logging

_logger = logging.getLogger(__name__)


class Storage(object):

    def __init__(self, cr, uid, model_name, field_name, record, config):
        self.cr = cr
        self.uid = uid
        self.pool = record._model.pool
        self.field_name = field_name
        self.model_name = model_name
        self.config = config


class FileSystemStorage(Storage):

    def _full_path(self, cr, uid, fname):
        return os.path.join(
            self.config['base_path'],
            self.cr.dbname,
            '%s-%s' % (self.model_name, self.field_name),
            fname)

    # Code extracted from Odoo V8 in ir_attachment.py
    # Copyright (C) 2004-2014 OPENERP SA
    # Licence AGPL V3
    def _get_path(self, cr, uid, bin_data):
        sha = hashlib.sha1(bin_data).hexdigest()
        # scatter files across 256 dirs
        # we use '/' in the db (even on windows)
        fname = sha[:2] + '/' + sha
        full_path = self._full_path(cr, uid, fname)
        dirname = os.path.dirname(full_path)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        return fname, full_path

    def _file_read(self, cr, uid, fname, bin_size=False):
        full_path = self._full_path(cr, uid, fname)
        r = ''
        try:
            if bin_size:
                r = os.path.getsize(full_path)
            else:
                r = open(full_path,'rb').read().encode('base64')
        except IOError:
            _logger.error("_read_file reading %s",full_path)
        return r

    def _file_write(self, cr, uid, value):
        bin_value = value.decode('base64')
        fname, full_path = self._get_path(cr, uid, bin_value)
        if not os.path.exists(full_path):
            try:
                with open(full_path, 'wb') as fp:
                    fp.write(bin_value)
            except IOError:
                _logger.error("_file_write writing %s", full_path)
        return fname

    def _file_delete(self, cr, uid, fname):
        obj = self.pool[self.model_name]
        count = obj.search(cr, 1, [
            ('%s_uid' % self.field_name, '=', fname),
            ], count=True)
        full_path = self._full_path(cr, uid, fname)
        if count <= 1 and os.path.exists(full_path):
            try:
                os.unlink(full_path)
            except OSError:
                _logger.error("_file_delete could not unlink %s",full_path)
            except IOError:
                # Harmless and needed for race conditions
                _logger.error("_file_delete could not unlink %s",full_path)
    # END of extraction

    def add(self, value):
        if not value:
            return {}
        file_size = sys.getsizeof(value.decode('base64'))
        _logger.debug('Add binary to model: %s, field: %s'
                      % (self.model_name, self.field_name))
        binary_uid = self._file_write(self.cr, self.uid, value)       
        return {
            'binary_uid': binary_uid,
            'file_size': file_size,
            }

    def update(self, binary_uid, value):
        _logger.debug('Delete binary model: %s, field: %s, uid: %s'
                      % (self.model_name, self.field_name, binary_uid))
        self._file_delete(self.cr, self.uid, binary_uid)
        if not value:
            return {}
        return self.add(value)

    def get(self, binary_uid):
        return self._file_read(self.cr, self.uid, binary_uid)


class BinaryField(fields.function):

    def __init__(self, string, **kwargs):
        """Init a BinaryField field
        :params string: Name of the field
        :type string: str
        :params get_storage: Storage Class for processing the field
                            by default use the Storage on filesystem
        :type get_storage: :py:class`binary_field.Storage'
        :params config: configuration used by the storage class
        :type config: what you want it's depend of the Storage class
                      implementation
        """
        new_kwargs = {
            'type': 'binary',
            'string': string,
            'fnct_inv': self._fnct_write,
            'multi': False,
            }
        new_kwargs.update(kwargs)
        super(BinaryField, self).__init__(self._fnct_read, **new_kwargs)

    # No postprocess are needed
    # we already take care of bin_size option in the context
    def postprocess(self, cr, uid, obj, field, value=None, context=None):
        return value

    def _prepare_binary_meta(self, cr, uid, field_name, res, context=None):
        return {
            '%s_uid' % field_name: res.get('binary_uid'),
            '%s_file_size' % field_name: res.get('file_size'),
            }

    def _fnct_write(self, obj, cr, uid, ids, field_name, value, args,
                    context=None):
        if not isinstance(ids, (list, tuple)):
            ids = [ids]
        storage_obj = obj.pool['storage.configuration']
        for record in obj.browse(cr, uid, ids, context=context):
            storage = storage_obj.get_storage(cr, uid, field_name, record)
            binary_uid = record['%s_uid' % field_name]
            if binary_uid:
                res = storage.update(binary_uid, value)
            else:
                res = storage.add(value)
            vals = self._prepare_binary_meta(
                cr, uid, field_name, res, context=context)
            record.write(vals)
        return True

    def _fnct_read(self, obj, cr, uid, ids, field_name, args, context=None):
        result = {}
        storage_obj = obj.pool['storage.configuration']
        for record in obj.browse(cr, uid, ids, context=context):
            storage = storage_obj.get_storage(cr, uid, field_name, record)
            binary_uid = record['%s_uid' % field_name]
            if binary_uid:
                # Compatibility with existing binary field
                if context.get(
                    'bin_size_%s' % field_name, context.get('bin_size')
                ):
                    size = record['%s_file_size' % field_name]
                    result[record.id] = tools.human_size(long(size))
                else:
                    result[record.id] = storage.get(binary_uid)
            else:
                result[record.id] = None
        return result


class ImageField(BinaryField):

    def __init__(self, string, get_storage=Storage, config=None, 
            resize_based_on=None, height=64, width=64, **kwargs):
        """Init a ImageField field
        :params string: Name of the field
        :type string: str
        :params get_storage: Storage Class for processing the field
                            by default use the Storage on filesystem
        :type get_storage: :py:class`binary_field.Storage'
        :params config: configuration used by the storage class
        :type config: what you want it's depend of the Storage class
                      implementation
        :params resize_based_on: reference field that should be resized
        :type resize_based_on: str
        :params height: height of the image resized
        :type height: integer
        :params width: width of the image resized
        :type width: integer
        """
        super(ImageField, self).__init__(
            string,
            get_storage=get_storage,
            config=config,
            **kwargs)
        self.resize_based_on = resize_based_on
        self.height = height
        self.width = width

    def _fnct_write(self, obj, cr, uid, ids, field_name, value, args,
                    context=None):
        if context is None:
            context = {}
        related_field_name = obj._columns[field_name].resize_based_on

        # If we write an original image in a field with the option resized
        # We have to store the image on the related field and not on the
        # resized image field
        if related_field_name and not context.get('refresh_image_cache'):
            return self._fnct_write(
                obj, cr, uid, ids, related_field_name, value, args,
                context=context)
        else:
            super(ImageField, self)._fnct_write(
                obj, cr, uid, ids, field_name, value, args, context=context)
            
            for name, field in obj._columns.items():
                if isinstance(field, ImageField)\
                   and field.resize_based_on == field_name:
                    field._refresh_cache(
                        obj, cr, uid, ids, name, context=context)
        return True

    def _refresh_cache(self, obj, cr, uid, ids, field_name, context=None):
        """Refresh the cache of the small image
        :params ids: list of object id to refresh
        :type ids: list
        :params field_name: Name of the field to refresh the cache
        :type field_name: str
        """
        if context is None:
            context = {}
        if not isinstance(ids, (list, tuple)):
            ids = [ids]
        for record_id in ids:
            _logger.debug('Refreshing Image Cache from the field %s of object '
                          '%s id : %s' % (field_name, obj._name, record_id))
            field = obj._columns[field_name]
            record = obj.browse(cr, uid, record_id, context=context)
            original_image = record[field.resize_based_on]
            if original_image:
                size = (field.height, field.width)
                resized_image = image_resize_image(original_image, size)
            else:
                resized_image = None
            ctx = context.copy()
            ctx['refresh_image_cache'] = True
            self._fnct_write(obj, cr, uid, [record_id], field_name,
                             resized_image, None, context=ctx)


fields.BinaryField = BinaryField
fields.ImageField = ImageField


original__init__ = orm.BaseModel.__init__


def __init__(self, pool, cr):
    original__init__(self, pool, cr)
    if self.pool.get('binary.field.installed'):
        additional_field = {}
        for field_name in self._columns:
            field = self._columns[field_name]
            if isinstance(field, BinaryField):
                additional_field.update({
                    '%s_uid' % field_name:
                        fields.char('%s UID' % self._columns[field_name].string),
                    '%s_file_size' % field_name:
                        fields.integer(
                            '%s File Size' % self._columns[field_name].string),
                    })
                #import pdb; pdb.set_trace()
        self._columns.update(additional_field)


orm.BaseModel.__init__ = __init__


class BinaryFieldInstalled(orm.AbstractModel):
    _name = 'binary.field.installed'
