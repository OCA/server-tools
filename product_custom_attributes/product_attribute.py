# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
#   product_custom_attributes for OpenERP                                      #
#   Copyright (C) 2011 Akretion Benoît GUILLOT <benoit.guillot@akretion.com>  #
#                                                                             #
#   This program is free software: you can redistribute it and/or modify      #
#   it under the terms of the GNU Affero General Public License as            #
#   published by the Free Software Foundation, either version 3 of the        #
#   License, or (at your option) any later version.                           #
#                                                                             #
#   This program is distributed in the hope that it will be useful,           #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#   GNU Affero General Public License for more details.                       #
#                                                                             #
#   You should have received a copy of the GNU Affero General Public License  #
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
#                                                                             #
###############################################################################

from osv import osv, fields
import netsvc

class attribute_option(osv.osv):
    _name = "attribute.option"
    _description = "Attribute Option"
    _order="sequence"

    _columns = {
        'name': fields.char('Name', size=128, required=True),
        'attribute_id': fields.many2one('product.attribute', 'Product Attribute', required=True),
        'sequence': fields.integer('Sequence'),
    }

class product_attribute(osv.osv):

    _name = "product.attribute"
    _description = "Product Attribute"

    _inherits = {'ir.model.fields': 'field_id'}

    _columns = {
        'field_id': fields.many2one('ir.model.fields', 'Ir Model Fields', required=True, ondelete="cascade"),
        'attribute_type': fields.selection([('char','Char'),('text','Text'),('select','Select'),('multiselect','Multiselect'),('boolean','Boolean'),('integer','Integer'),('date','Date'),('datetime','Datetime'),('binary','Binary'),('float','Float')],'Type', required=True),
        'serialized': fields.boolean('Field serialized', help="If serialized, the field will be stocked in the serialized field : attribute_custom_tmpl or attribute_custom_variant depending on the field based_on"),
        'based_on': fields.selection([('product_template','Product Template'),('product_product','Product Variant')],'Based on', required=True),
        'option_ids': fields.one2many('attribute.option', 'attribute_id', 'Attribute Option'),
        'create_date': fields.datetime('Created date', readonly=True),
    }

    def create(self, cr, uid, vals, context=None):
        if vals.get('based_on') == 'product_template':
            vals['model_id'] = self.pool.get('ir.model').search(cr, uid, [('model', '=', 'product.template')],context=context)[0]
            serial_name = 'attribute_custom_tmpl'
        else:
            vals['model_id'] = self.pool.get('ir.model').search(cr, uid, [('model', '=', 'product.product')], context=context)[0]
            serial_name = 'attribute_custom_variant'
        if vals.get('serialized'):
            vals['serialization_field_id'] = self.pool.get('ir.model.fields').search(cr, uid, [('name', '=', serial_name)], context=context)[0]
        if vals['attribute_type'] == 'select':
            vals['ttype'] = 'many2one'
            vals['relation'] = 'attribute.option'
        elif vals['attribute_type'] == 'multiselect':
            vals['ttype'] = 'many2many'
            vals['relation'] = 'attribute.option'
            if not vals.get('serialized'):
                raise osv.except_osv(_('Create Error'), _("The field serialized should be ticked for a multiselect field !"))
        else:
            vals['ttype'] = vals['attribute_type']
        vals['state'] = 'manual'
        return super(product_attribute, self).create(cr, uid, vals, context)

    def onchange_field_description(self, cr, uid, ids, field_description, context=None):
        name = 'x_'
        if field_description:
            name = 'x_%s' % field_description.replace(' ', '_').lower()
        return  {'value' : {'name' : name}}

class attribute_location(osv.osv):

    _name = "attribute.location"
    _description = "Attribute Location"
    _order="sequence"

    _inherits = {'product.attribute': 'attribute_id'}

    _columns = {
        'attribute_id': fields.many2one('product.attribute', 'Product Attribute', required=True, ondelete="cascade"),
        'attribute_set_id': fields.many2one('attribute.set', 'Attribute Set', required=True),
        'attribute_group_id': fields.many2one('attribute.group', 'Attribute Group', required=True),
        'sequence': fields.integer('Sequence'),
    }

class attribute_group(osv.osv):

    _name= "attribute.group"
    _description = "Attribute Group"
    _order="sequence"

    _columns = {
        'name': fields.char('Name', size=128, required=True),
        'attribute_set_id': fields.many2one('attribute.set', 'Attribute Set', required=True),
        'attribute_ids': fields.one2many('attribute.location', 'attribute_group_id', 'Attributes'),
        'sequence': fields.integer('Sequence'),
    }


class attribute_set(osv.osv):

    _name = "attribute.set"
    _description = "Attribute Set"

    _columns = {
        'name': fields.char('Name', size=128, required=True),
        'attribute_group_ids': fields.one2many('attribute.group', 'attribute_set_id', 'Attribute Groups'),
    }
