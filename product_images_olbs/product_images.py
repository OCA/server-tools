# -*- encoding: utf-8 -*-
#########################################################################
# Copyright (C) 2009  Sharoon Thomas, Open Labs Business solutions      #
# Copyright (C) 2011 Akretion Sébastien BEAU sebastien.beau@akretion.com#
#                                                                       #
#This program is free software: you can redistribute it and/or modify   #
#it under the terms of the GNU General Public License as published by   #
#the Free Software Foundation, either version 3 of the License, or      #
#(at your option) any later version.                                    #
#                                                                       #
#This program is distributed in the hope that it will be useful,        #
#but WITHOUT ANY WARRANTY; without even the implied warranty of         #
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
#GNU General Public License for more details.                           #
#                                                                       #
#You should have received a copy of the GNU General Public License      #
#along with this program.  If not, see <http://www.gnu.org/licenses/>.  #
#########################################################################
from osv import osv, fields
import base64, urllib
from tools.translate import _
import os
import netsvc

#TODO find a good solution in order to roll back changed done on file system
#TODO add the posibility to move from a store system to an other (example : moving existing image on database to file system)

class product_images(osv.osv):
    "Products Image gallery"
    _name = "product.images"
    _description = __doc__
    _table = "product_images"
    
    def unlink(self, cr, uid, ids, context=None):
        if not isinstance(ids, list):
            ids=[ids]
        local_media_repository = self.pool.get('res.company').get_local_media_repository(cr, uid, context=context)
        if local_media_repository:
            for image in self.browse(cr, uid, ids, context=context):
                path = os.path.join(local_media_repository, image.product_id.default_code, image.name)
                if os.path.isfile(path):
                    os.remove(path)          
        return super(product_images, self).unlink(cr, uid, ids, context=context)

    def create(self, cr, uid, vals, context=None):
        if vals.get('name', False) and not vals.get('extention', False):
            vals['name'], vals['extention'] = os.path.splitext(vals['name'])
        return super(product_images, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if not isinstance(ids, list):
            ids=[ids]
        if vals.get('name', False) and not vals.get('extention', False):
            vals['name'], vals['extention'] = os.path.splitext(vals['name'])
        if vals.get('name', False) or vals.get('extention', False):
            local_media_repository = self.pool.get('res.company').get_local_media_repository(cr, uid, context=context)
            if local_media_repository:
                old_images = self.browse(cr, uid, ids, context=context)
                res=[]
                for old_image in old_images:
                    if vals.get('name', False) and (old_image.name != vals['name']) or vals.get('extention', False) and (old_image.extention != vals['extention']):
                        old_path = os.path.join(local_media_repository, old_image.product_id.default_code, '%s%s' %(old_image.name, old_image.extention))
                        res.append(super(product_images, self).write(cr, uid, old_image.id, vals, context=context))
                        if 'file' in vals:
                            #a new image have been loaded we should remove the old image
                            #TODO it's look like there is something wrong with function field in openerp indeed the preview is always added in the write :(
                            if os.path.isfile(old_path):
                                os.remove(old_path)
                        else:
                            #we have to rename the image on the file system
                            if os.path.isfile(old_path):
                                os.rename(old_path, os.path.join(local_media_repository, old_image.product_id.default_code, '%s%s' %(old_image.name, old_image.extention)))      
                return res
        return super(product_images, self).write(cr, uid, ids, vals, context=context)

    def get_image(self, cr, uid, id, context=None):
        each = self.read(cr, uid, id, ['link', 'url', 'name', 'file_db_store', 'product_id', 'name', 'extention'])
        if each['link']:
            (filename, header) = urllib.urlretrieve(each['url'])
            f = open(filename , 'rb')
            img = base64.encodestring(f.read())
            f.close()
        else:
            local_media_repository = self.pool.get('res.company').get_local_media_repository(cr, uid, context=context)
            if local_media_repository:
                product_code = self.pool.get('product.product').read(cr, uid, each['product_id'][0], ['default_code'])['default_code']
                full_path = os.path.join(local_media_repository, product_code, '%s%s'%(each['name'], each['extention']))
                if os.path.exists(full_path):
                    try:
                        f = open(full_path, 'rb')
                        img = base64.encodestring(f.read())
                        f.close()
                    except Exception, e:
                        logger = netsvc.Logger()
                        logger.notifyChannel('product_images', netsvc.LOG_ERROR, "Can not open the image %s, error : %s" %(full_path, e))
                        return False
                else:
                    logger = netsvc.Logger()
                    logger.notifyChannel('product_images', netsvc.LOG_ERROR, "The image %s doesn't exist " %full_path)
                    return False
            else:
                img = each['file_db_store']
        return img
    
    def _get_image(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for each in ids:
            res[each] = self.get_image(cr, uid, each, context=context)
        return res

    def _check_filestore(self, image_filestore):
        '''check if the filestore is created, if not it create it automatically'''
        try:
            if not os.path.isdir(image_filestore):
                os.makedirs(image_filestore)
        except Exception, e:
            raise osv.except_osv(_('Error'), _('The image filestore can not be created, %s'%e))
        return True

    def _save_file(self, path, filename, b64_file):
        """Save a file encoded in base 64"""
        full_path = os.path.join(path, filename)
        self._check_filestore(path)
        ofile = open(full_path, 'w')
        try:
            ofile.write(base64.decodestring(b64_file))
        finally:
            ofile.close()
        return True

    def _set_image(self, cr, uid, id, name, value, arg, context=None):
        local_media_repository = self.pool.get('res.company').get_local_media_repository(cr, uid, context=context)
        if local_media_repository:
            image = self.browse(cr, uid, id, context=context)
            return self._save_file(os.path.join(local_media_repository, image.product_id.default_code), '%s%s'%(image.name, image.extention), value)
        return self.write(cr, uid, id, {'image' : value}, context=context)

    _columns = {
        'name':fields.char('Image Title', size=100, required=True),
        'extention': fields.char('file extention', size=4),
        'link':fields.boolean('Link?', help="Images can be linked from files on your file system or remote (Preferred)"),
        'file_db_store':fields.binary('Image stored in database'),
        'file':fields.function(_get_image, fnct_inv=_set_image, type="image", method=True, filters='*.png,*.jpg,*.gif'),
        'url':fields.char('File Location', size=250),
        'comments':fields.text('Comments'),
        'product_id':fields.many2one('product.product', 'Product')
    }

    _defaults = {
        'link': lambda *a: True,
    }

    _sql_constraints = [('uniq_name_product_id', 'UNIQUE(product_id, name)',
                _('A product can have only one image with the same name'))]

product_images()
