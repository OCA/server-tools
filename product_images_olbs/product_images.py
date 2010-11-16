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

class product_images(osv.osv):
    "Products Image gallery"
    _name = "product.images"
    _description = __doc__
    _table = "product_images"
    
    def get_image(self, cr, uid, id):
        each = self.read(cr, uid, id, ['link', 'filename', 'image'])
        if each['link']:
            (filename, header) = urllib.urlretrieve(each['filename'])
            f = open(filename , 'rb')
            img = base64.encodestring(f.read())
            f.close()
        else:
            img = each['image']
        return img
    
    def _get_image(self, cr, uid, ids, field_name, arg, context={}):
        res = {}
        for each in ids:
            res[each] = self.get_image(cr, uid, each)
        return res
    
    _columns = {
        'name':fields.char('Image Title', size=100, required=True),
        'link':fields.boolean('Link?', help="Images can be linked from files on your file system or remote (Preferred)"),
        'image':fields.binary('Image', filters='*.png,*.jpeg,*.gif'),
        'filename':fields.char('File Location', size=250),
        'preview':fields.function(_get_image, type="binary", method=True),
        'comments':fields.text('Comments'),
        'product_id':fields.many2one('product.product', 'Product')
    }
product_images()
