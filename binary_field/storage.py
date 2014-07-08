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

from .fields import FileSystemStorage
from openerp.osv import fields, orm


class StorageConfiguration(orm.Model):
    _name = 'storage.configuration'
    _description = 'storage configuration'
   
    def _get_storage_map_class(self, cr, uid, context=None):
        return {
            'filesystem' : FileSystemStorage,
            }

    def _get_class(self, cr, uid, type, context=None):
        map_class = self._get_storage_map_class(cr, uid, context=context)
        return map_class[type]

    def _get_config(self, cr, uid, model_name, field_name, context=None):
        field_obj = self.pool['ir.model.fields']
        field_id = field_obj.search(cr, uid, [
            ('model', '=', model_name),
            ('name', '=', field_name),
            ], context=context)
        if not field_id:
            raise orm.except_orm(
                _('Dev Error'),
                _('The field %s with do not exist on the model %s')
                %(field, model))
        else:
            field_id = field_id[0]
        field = field_obj.browse(cr, uid, field_id, context=context)
        storage_id = field.storage_id.id
        if not storage_id:
            storage_id = self.search(cr, uid, [
                ('is_default', '=', True),
                ], context=context)
            if storage_id:
                storage_id = storage_id[0]
            else:
                raise orm.except_orm(
                    _('User Error'),
                    _('There is not default storage configuration, '
                      'please add one'))
        return self.read(cr, uid, storage_id, self._columns.keys(),
                         context=context)

    def get_storage(self, cr, uid, field_name, record, context=None):
        model_name = record._name
        config = self._get_config(cr, uid, record._name, field_name)
        storage_class = self._get_class(
            cr, uid, config['type'], context=context)
        return storage_class(cr, uid, model_name, field_name, record, config)

    def _get_storage_type(self, cr, uid, context=None):
        return [('filesystem', 'File System')]

    def __get_storage_type(self, cr, uid, context=None):
        return self._get_storage_type(cr, uid, context=context)

    def _remove_default(self, cr, uid, context=None):
        conf_id = self.search(cr, uid, [
            ('is_default', '=', True),
            ], context=context)
        self.write(cr, uid, conf_id, {
            'is_default': False,
            }, context=context)

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if vals.get('is_default'):
            self._remove_default(cr, uid, context=context)
        return super(StorageConfiguration, self).\
            create(cr, uid, vals, context=context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        if vals.get('is_default'):
            self._remove_default(cr, uid, context=context)
        return super(StorageConfiguration, self).\
            write(cr, uid, ids, vals, context=context)

    _columns = {
        'name': fields.char('Name'),
        'type': fields.selection(
            __get_storage_type,
            'Type',
            help='Type of storage'),
        'base_path': fields.char('Path'),
        'is_default': fields.boolean(
            'Is default',
            help=('Tic that box in order to select '
                 'the default storage configuration')),
        'external_storage_server': fields.boolean(
            'External Storage Server',
            help=('Tic that box if you want to server the file with an '
                 'external server. For example, if you choose the storage '
                 'on File system, the binary file can be serve directly with '
                 'nginx or apache...')),
        'base_external_url': fields.char(
            'Base external URL',
            help=('When you use an external server for storing the binary '
                  'you have to enter the base of the url where the binary can'
                  ' be accesible.')),
    }
