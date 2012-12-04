# -*- encoding: utf-8 -*-
#################################################################################
#                                                                               #
#    product_multi_price for OpenERP                                          #
#    Copyright (C) 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>   #
#                                                                               #
#    This program is free software: you can redistribute it and/or modify       #
#    it under the terms of the GNU Affero General Public License as             #
#    published by the Free Software Foundation, either version 3 of the         #
#    License, or (at your option) any later version.                            #
#                                                                               #
#    This program is distributed in the hope that it will be useful,            #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              #
#    GNU Affero General Public License for more details.                        #
#                                                                               #
#    You should have received a copy of the GNU Affero General Public License   #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.      #
#                                                                               #
#################################################################################

from openerp.osv.orm import Model
from openerp.osv import fields
from openerp.osv.osv import except_osv
from tools.translate import _

#TODO


class product_price_fields(Model):
    _name = "product.price.fields"
    _description = "product price fields"
    _columns = {
        'name': fields.related('price_field_id', 'field_description', type='char', size=64, string='Field Label', store=True),
        'field_name': fields.related('price_field_id', 'name', type='char', size=64, string='Field Name', store=True, help ="you can chose the field name by default it will be build with the name of the field replacing the space by '_' and adding x_pm_ add the start"),
        'price_field_id' : fields.many2one('ir.model.fields', 'Field ID', domain = [('model', '=', 'product.product'), ('ttype', '=', 'float')]),
        'sequence' : fields.integer('Sequence', help="The product 'variants' code will use order the field on the product view"),
        'tax_included': fields.boolean('Tax included'),
        'basedon_field_id' : fields.many2one('ir.model.fields', 'Based on Field ID', domain = [('model', '=', 'product.product'), ('ttype', '=', 'selection')]),
        'product_coef_field_id' : fields.many2one('ir.model.fields', 'Product Coef Field ID', domain = [('model', '=', 'product.product'), ('ttype', '=', 'float')]),
        'categ_coef_field_id' : fields.many2one('ir.model.fields', 'Category Coef Field ID', domain = [('model', '=', 'product.category'), ('ttype', '=', 'float')]),
        'default_basedon':fields.selection([('categ_coef','Price on category coefficient'),('product_coef','Price on product coefficient'),('manual','Manual price')], 'Based on by default', required=True),
        'currency_id': fields.many2one('res.currency', "Currency", required=True, help="The currency the field is expressed in."),
        'inc_price_field_id' : fields.many2one('ir.model.fields', 'Price Included Field ID', domain = [('model', '=', 'product.product'), ('ttype', '=', 'float')]),
        }

    def _get_currency(self, cr, uid, ctx):
        comp = self.pool.get('res.users').browse(cr, uid, uid).company_id
        if not comp:
            comp_id = self.pool.get('res.company').search(cr, uid, [])[0]
            comp = self.pool.get('res.company').browse(cr, uid, comp_id)
        return comp.currency_id.id

    _defaults = {
        "currency_id": _get_currency
    }

    _order = "sequence, name"

    def _create_price_type(self, cr, uid, vals, context=None):
        field = (vals.get('field_name', False) or 'x_pm_price_' + vals['name'].replace(' ', '_').replace('-', '_')).lower()
        name = (_('Price')) + ' ' + (vals.get('field_name', False) or vals['name']).capitalize()
        type_obj = self.pool.get('product.price.type')
        price_type_ids = type_obj.search(cr, uid, [
                                        ('name', '=', name),
                                        ('field', '=', field)], context=context)
        if not price_type_ids:
            type_vals = {
                        'name': name,
                        'active': True,
                        'field': field,
                        'currency_id': vals['currency_id']
                        }
            price_type_id = type_obj.create(cr, uid, type_vals, context=context)
        else:
            price_type_id = price_type_ids[0]
        return price_type_id

    def _create_price_list(self, cr, uid, vals, price_type_id, context=None):
        pricelist_obj = self.pool.get('product.pricelist')
        name = (vals.get('field_name', False) or vals['name']).capitalize()
        pricelist_ids = pricelist_obj.search(cr, uid, [
                                                ('name', '=', ((_('Price list')) + ' ' + name)),
                                                ('type', '=', 'sale')], context=context)
        if not pricelist_ids:
            items = [(0,0,{
                        'name' : (_('Default')) + ' '+ name,
                        'sequence': 5,
                        'base':price_type_id,
                        'min_quantity':0,
                        })]
            pricelist_version = [(0,0,{
                        'name': (_('Version')) + ' ' + name,
                        'active': True,
                        'items_id': items,
                        })]
            list_vals = {
                        'name': (_('Price list')) + ' ' + name,
                        'active': True,
                        'type': 'sale',
                        'version_id': pricelist_version,
                        'currency_id': vals['currency_id'],
                        #TODO support multi_company pricelists
                        }
            pricelist_id = pricelist_obj.create(cr, uid, list_vals, context=context)
        else:
            pricelist_id = pricelist_ids[0]
        return pricelist_id

    def create(self, cr, uid, vals, context=None):
        product_model_id = self.pool.get('ir.model').search(cr, uid, [('model', '=', 'product.product')])[0]
        categ_model_id = self.pool.get('ir.model').search(cr, uid, [('model', '=', 'product.category')])[0]
        if vals.get('price_field_id', False):
            return super(product_price_fields, self).create(cr, uid, vals, context)
        exist_id = False
        if vals.get('field_name', False):
            print 'field name'
            exist_id = self.pool.get('ir.model.fields').search(cr, uid, [('name', '=', vals['field_name'])])
            if not exist_id and vals['field_name'][0:2] != 'x_':
                raise except_osv(_('User Error'), _("Please prefix the field name by x_ as it is a custom field"))
        field_list = ['price', 'inc_price', 'basedon','product_coef','categ_coef']
        product_ids = self.pool.get('product.product').search(cr, uid, [], context=context)
        for field in field_list:
            if exist_id and field == 'price':
                vals[field +'_field_id'] = exist_id[0]
                if not vals.get('name', False):
                    vals['name'] = vals['field_name']
                del vals['field_name']
            else:
                if field == 'categ_coef':
                    model_id = categ_model_id
                    model = 'product.category'
                else:
                    model_id = product_model_id
                    model = 'product.product'
                field_vals = {
                    'name': (vals.get('field_name', False) or 'x_pm_' + field + '_' + vals['name'].replace(' ', '_').replace('-', '_')).lower() ,
                    'model_id':model_id,
                    'model':model,
                    'field_description': (vals.get('field_name', False) or vals['name']).capitalize() + ' ' + field,
                    'state': 'manual'
                }
                if field in ['price', 'inc_price', 'product_coef','categ_coef']:
                    field_vals['ttype'] = 'float'
                if field == 'basedon':
                    field_vals['ttype'] = 'selection'
                    field_vals['selection'] = "[('categ_coef','Price on category coefficient'),('product_coef','Price on product coefficient'),('manual','Manual price')]"
                    field_vals['required'] = True
                vals[field + '_field_id'] = self.pool.get('ir.model.fields').create(cr, uid, field_vals)
                default_vals={}
                if field == 'basedon' and vals.get('default_basedon', False):
                    default_vals[field_vals['name']] = vals['default_basedon']
                    self.pool.get('product.product').write(cr, uid, product_ids, default_vals, context=context)
        if not exist_id:
            if not vals.get('currency_id'):
                vals['currency_id'] = self._get_currency(cr, uid, context)
            price_type_id = self._create_price_type(cr, uid, vals, context=context)
            price_list = self._create_price_list(cr, uid, vals, price_type_id, context=context)
        if vals.get('field_name', False):
            del vals['field_name']
        del vals['name']
        return super(product_price_fields, self).create(cr, uid, vals, context)

    def unlink(self, cr, uid, ids, context=None):
        for price_field in self.browse(cr, uid, ids, context=context):
            price_field.price_field_id.unlink()
            price_field.basedon_field_id.unlink()
            price_field.product_coef_field_id.unlink()
            price_field.categ_coef_field_id.unlink()
        return super(product_price_fields, self).unlink(cr, uid, ids, context=context)
