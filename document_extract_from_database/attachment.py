# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Julius Network Solutions SARL <contact@julius.fr>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp.osv import orm, fields
import base64

class document_multiple_action(orm.TransientModel):
    _name = "document.multiple.action"
    _description = "Multiple action on document"

    def write_again(self, cr, uid, ids, context=None):
        if context is None: context = {}
        document_obj = self.pool.get('ir.attachment')
        document_ids = context.get('active_ids')
        if document_ids:
            document_obj.write_again(cr, uid, document_ids, context=context)
        return True

class document_file(orm.Model):
    _inherit = 'ir.attachment'

    def _write_again(self, cr, uid, id, context=None):
        current_data = self.browse(cr, uid, id, context=context)
        location = self.pool.get('ir.config_parameter').\
            get_param(cr, uid, 'ir_attachment.location')
        if current_data.db_datas and location:
            vals = {
                'datas': base64.encodestring(current_data.db_datas),
                'db_datas': False,
            }
            self.write(cr, uid, id, vals, context=context)
        return True

    def write_again(self, cr, uid, ids, context=None):
        if context==None:
            context = {}
        for document_id in ids:
            self._write_again(cr, uid, document_id, context=context)
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: