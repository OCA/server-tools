# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from osv import osv, fields
from tools.translate import _
import netsvc

from ftplib import FTP
import os

class product_icecat(osv.osv):
    _name = "product.icecat"

product_icecat()

class product_icecat_mapline(osv.osv):
    _name = "product.icecat.mapline"
    _description = "Icecat Mapline Configuration"

    _columns = {
        'name': fields.char('XML Field', size=32, required=True, help='Insert ID Category from Icecat'),
        'model_id': fields.many2one('ir.model','OpenERP Model'),
        'field_id': fields.many2one('ir.model.fields','OpenERP Field', required=True),
        'icecat_id': fields.many2one('product.icecat','Icecat'),
    }

    _defaults = {
        'model_id': lambda self, cr, uid, c: self.pool.get('ir.model').search(cr, uid, [('model', '=', 'product.product')])[0],
    }

product_icecat_mapline()

class product_icecat(osv.osv):
    _name = "product.icecat"
    _description = "Icecat Configuration"

    def check_ftp(self, cr, uid, ids, context):
        if context is None:
            context = {}

        for id in ids:
            icecat = self.browse(cr, uid, id)

            try: ftp = FTP(icecat.ftpip)
            except:
                raise osv.except_osv(_('Error !'), _("IP FTP connection was not successfully!"))

            try: ftp.login(icecat.ftpusername, icecat.ftppassword)
            except:
                raise osv.except_osv(_('Error !'), _("Username/password FTP connection was not successfully!"))

            ftp.quit()
            raise osv.except_osv(_('Ok !'), _("FTP connection was successfully!"))

    _columns = {
        'name': fields.char('Name', size=32, required=True),
        'username': fields.char('User Name', size=32, required=True),
        'password': fields.char('Password', size=32, required=True),
        'active': fields.boolean('Active'),
        'mapline_ids': fields.one2many('product.icecat.mapline','icecat_id','Mapline'),
        'ftp': fields.boolean('Active'),
        'ftpip': fields.char('IP', size=256),
        'ftpdirectory': fields.char('Directory', size=256, help='If not use directory, insert . (point). If use directory, path FTP dir'),
        'ftpusername': fields.char('Username', size=32),
        'ftppassword': fields.char('Password', size=32),
        'ftpurl': fields.char('URL', size=256, help='URL FTP Dir: http://domain/directory/'),
    }

    _defaults = {
        'active': lambda *a: 1,
    }

    def create(self, cr, uid, vals, context={}):
        if vals.get('active',False):
            actv_ids =  self.search(cr, uid, [('active','=',True)])
            if len(actv_ids):
                raise osv.except_osv(_('Error!'), _('They are other icecat configuration with "Active" field checked. Only one configuration is avaible for active field.'))
        return super(product_icecat, self).create(cr, uid, vals, context)

product_icecat()


