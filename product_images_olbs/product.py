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
from osv import osv,fields
from tools.translate import _
import os

class product_product(osv.osv):
    _inherit = "product.product"
    _columns = {
        'image_ids':fields.one2many(
                'product.images',
                'product_id',
                'Product Images'
        ),
        'default_code' : fields.char('Reference', size=64, require='True'),
    }

    def write(self, cr, uid, ids, vals, context=None):
        #note that write on default code can be only done on one id, if it's multiple id it will raise an error indeed default code should be uniq
        if vals.get('default_code', False):
            user = self.pool.get('res.users').browse(cr, uid, uid)
            company = user.company_id
            if company.local_media_repository:
                if isinstance(ids, list):
                    id =ids[0]
                else:
                    id=ids
                old_default_code = self.read(cr, uid, id, ['default_code'], context=context)['default_code']
                res = super(product_product, self).write(cr, uid, ids, vals, context=context)
                if old_default_code != vals['default_code']:
                    old_path = os.path.join(company.local_media_repository, old_default_code)
                    if os.path.isdir(old_path):
                        os.rename(old_path,  os.path.join(company.local_media_repository, vals['default_code']))
                return res
        return super(product_product, self).write(cr, uid, ids, vals, context=context)

    #This constraint should be by default in openerp 
    _sql_constraints = [('default_code', 'UNIQUE(defaut_code)',
                _('Default code should be uniq'))]
    
product_product()
