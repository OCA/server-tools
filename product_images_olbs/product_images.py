#########################################################################
# Copyright (C) 2009  Sharoon Thomas, Open Labs Business solutions      #
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

class product_images(osv.osv):
    "Products Image gallery"
    _name = "product.images"
    _description = __doc__
    _table = "product_images"
    
    def unlink(self, cr, uid, ids, context=None):
        #TODO
        return super(product_images, self).unlink(cr, uid, ids, context=context)

    def get_image(self, cr, uid, id):
        each = self.read(cr, uid, id, ['link', 'filename', 'image', 'product_id', 'name'])
        if each['link']:
            (filename, header) = urllib.urlretrieve(each['filename'])
            f = open(filename , 'rb')
            img = base64.encodestring(f.read())
            f.close()
        else:
            user = self.pool.get('res.users').browse(cr, uid, uid)
            company = user.company_id
            if company.local_media_repository:
                product_code = self.pool.get('product.product').read(cr, uid, each['product_id'][0], ['default_code'])['default_code']
                full_path = os.path.join(company.local_media_repository, product_code, each['name'])
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
                img = each['image']
        return img
    
    def _get_image(self, cr, uid, ids, field_name, arg, context={}):
        res = {}
        for each in ids:
            res[each] = self.get_image(cr, uid, each)
        return res

    def _check_filestore(self, image_filestore):
        '''check if the filestore is created, if not it create it automatically'''
        print 'create directory', image_filestore
        try:
            if not os.path.isdir(image_filestore):
                print 'create the directory'
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
            print 'write'
        finally:
            ofile.close()
        return True

    def _set_image(self, cr, uid, id, name, value, arg, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        company = user.company_id
        if company.local_media_repository:
            image = self.browse(cr, uid, id, context=context)
            return self._save_file(os.path.join(company.local_media_repository, image.product_id.default_code), image.name , value)
        return self.write(cr, uid, id, {'image' : value}, context=context)

    _columns = {
        'name':fields.char('Image Title', size=100, required=True),
        'link':fields.boolean('Link?', help="Images can be linked from files on your file system or remote (Preferred)"),
        'image':fields.binary('Image', filters='*.png,*.jpg,*.gif'),
        'filename':fields.char('File Location', size=250),
        'preview':fields.function(_get_image, fnct_inv=_set_image, type="image", method=True),
        'comments':fields.text('Comments'),
        'product_id':fields.many2one('product.product', 'Product')
    }

    _defaults = {
        'link': lambda *a: True,
    }

    _sql_constraints = [('uniq_name_product_id', 'UNIQUE(product_id, name)',
                _('A product can have only one image with the same name'))]

product_images()
