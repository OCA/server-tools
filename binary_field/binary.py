# -*- coding: utf-8 -*-
###############################################################################
#
#   Module for OpenERP
#   OpenERP, Open Source Management Solution
#   Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
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
from openerp.tools.translate import _
from openerp.addons.base.ir import ir_attachment
import os
import logging

_logger = logging.getLogger(__name__)


class BinaryBinary(orm.Model):
    _name = 'binary.binary'
    _description = 'binary.binary'

    _columns = {
        #'name': fields.char('Name',size=256, required=True),
        'store_fname': fields.char('Stored Filename', size=256),
        #'extension': fields.char('Extension', size=4),
        'file_size': fields.integer('File Size'),
    }

    def _get_location(self, cr, uid):
        base_location = self.pool.get('ir.config_parameter').\
            get_param(cr, uid, 'binary.location')
        if not base_location:
            raise orm.except_orm(
                _('Configuration Error'),
                _('The "binary.location" is empty, please fill it in'
                  'Configuration > Parameters > System Parameters'))
        return base_location

    def add(self, cr, uid, value, field_key, context=None):
        if not value:
            return None
        base_location = self._get_location(cr, uid)
        # Hack for passing the field_key in the full path
        location = (base_location, field_key)
        file_size = len(value.decode('base64'))
        fname = self._file_write(cr, uid, location, value)
        return self.create(cr, uid, {
            'store_fname': fname,
            'file_size': file_size,
            }, context=context)

    def update(self, cr, uid, binary_id, value, field_key, context=None):
        binary = self.browse(cr, uid, binary_id, context=context)
        base_location = self._get_location(cr, uid)
        # Hack for passing the field_key in the full path
        location = (base_location, field_key)
        self._file_delete(cr, uid, location, binary.store_fname)
        if not value:
            return None
        fname = self._file_write(cr, uid, location, value)
        file_size = len(value.decode('base64'))
        self.write(cr, uid, binary_id, {
            'store_fname': fname,
            'file_size': file_size,
            }, context=context)
        return True
    
    def get_content(self, cr, uid, field_key, binary_id, context=None):
        binary = self.browse(cr, uid, binary_id, context=context)
        base_location = self._get_location(cr, uid)
        # Hack for passing the field_key in the full path
        location = (base_location, field_key)
        return self._file_read(cr, uid, location, binary.store_fname)

    def _file_read(self, cr, uid, location, fname):
        return self.pool['ir.attachment']._file_read(cr, uid, location, fname)

    def _file_write(self, cr, uid, location, value):
        return self.pool['ir.attachment']._file_write(cr, uid, location, value)

    def _file_delete(self, cr, uid, location, fname):
        return self.pool['ir.attachment']._file_delete(cr, uid, location, fname)


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
