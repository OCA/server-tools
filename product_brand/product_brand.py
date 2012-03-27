# -*- encoding: utf-8 -*-
from osv import osv, fields
import  os

class product_brand(osv.osv):
    _name = 'product.brand'
    _columns = {
        'name': fields.char('Brand Name',size=32),
        'description': fields.text('Description',translate=True),
        'logo_id' : fields.many2one('ir.attachment','Logo', help='Select picture file'),
        'partner_id' : fields.many2one('res.partner','partner', help='Select a partner for this brand if it exist'),
    }

product_brand()

class product_product(osv.osv):
    _name = 'product.product'
    _inherit = 'product.product'
    _columns = {
        'product_brand_id' : fields.many2one('product.brand','Brand', help='Select a brand for this product'),
    }

product_product()

class product_template(osv.osv):
    _name = 'product.template'
    _inherit = 'product.template'
    _columns = {
        'product_brand_id' : fields.many2one('product.brand','Brand', help='Select a brand for this product'),
    }

product_template()