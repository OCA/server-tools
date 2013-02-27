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

from openerp.osv.orm import Model
from openerp.osv import osv
from openerp.osv import fields
from openerp.osv.osv import except_osv
from lxml import etree
from openerp.tools.translate import _
from unidecode import unidecode # Debian package python-unidecode

class attribute_option(Model):
    _name = "attribute.option"
    _description = "Attribute Option"
    _order="sequence"

    _columns = {
        'name': fields.char('Name', size=128, translate=True, required=True),
        'value_ref': fields.reference('Reference', selection=[], size=128),
        'attribute_id': fields.many2one('product.attribute', 'Product Attribute', required=True),
        'sequence': fields.integer('Sequence'),
    }

    def name_change(self, cr, uid, ids, name, relation_model_id, context=None):
        if relation_model_id:
            warning = {'title': _('Error!'), 'message': _("Use the 'Change Options' button instead to select appropriate model references'")}
            return {"value": {"name": False}, "warning": warning}
        else:
            return True

class attribute_option_wizard(osv.osv_memory):
    _name = "attribute.option.wizard"
    _rec_name = 'attribute_id'

    _columns = {
        'attribute_id': fields.many2one('product.attribute', 'Product Attribute', required=True),
    }

    _defaults = {
        'attribute_id': lambda self, cr, uid, context: context.get('attribute_id', False)
    }

    def validate(self, cr, uid, ids, context=None):
        return True

    def create(self, cr, uid, vals, context=None):
        attr_obj = self.pool.get("product.attribute")
        attr = attr_obj.browse(cr, uid, vals['attribute_id'])
        op_ids = [op.id for op in attr.option_ids]
        opt_obj = self.pool.get("attribute.option")
        opt_obj.unlink(cr, uid, op_ids)
        for op_id in (vals.get("option_ids") and vals['option_ids'][0][2] or []):
            model = attr.relation_model_id.model
            name = self.pool.get(model).name_get(cr, uid, [op_id], context)[0][1]
            opt_obj.create(cr, uid, {
                'attribute_id': vals['attribute_id'],
                'name': name,
                'value_ref': "%s,%s" % (attr.relation_model_id.model, op_id)
            })
        res = super(attribute_option_wizard, self).create(cr, uid, vals, context)
        return res

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        res = super(attribute_option_wizard, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar, submenu)
        if context and context.get("attribute_id"):
            attr_obj = self.pool.get("product.attribute")
            model_id = attr_obj.read(cr, uid, [context.get("attribute_id")], ['relation_model_id'])[0]['relation_model_id'][0]
            relation = self.pool.get("ir.model").read(cr, uid, [model_id], ["model"])[0]["model"]
            res['fields'].update({'option_ids': {
                            'domain': [],
                            'string': "Options",
                            'type': 'many2many',
                            'relation': relation,
                            'required': True,
                            }
                        })
            eview = etree.fromstring(res['arch'])
            options = etree.Element('field', name='option_ids', colspan='6')
            placeholder = eview.xpath("//separator[@string='options_placeholder']")[0]
            placeholder.getparent().replace(placeholder, options)
            res['arch'] = etree.tostring(eview, pretty_print=True)
        return res


class product_attribute(Model):
    _name = "product.attribute"
    _description = "Product Attribute"
    _inherits = {'ir.model.fields': 'field_id'}

    def relation_model_id_change(self, cr, uid, ids, relation_model_id, option_ids, context=None):
        "removed selected options as they would be inconsistent" 
        return {'value': {'option_ids': [(2, i[1]) for i in option_ids]}}

    def button_add_options(self, cr, uid, ids, context=None):
        return {
            'context': "{'attribute_id': %s}" % (ids[0]),
            'name': _('Options Wizard'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'attribute.option.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    _columns = {
        'field_id': fields.many2one('ir.model.fields', 'Ir Model Fields', required=True, ondelete="cascade"),
        'attribute_type': fields.selection([('char','Char'),
                                            ('text','Text'),
                                            ('select','Select'),
                                            ('multiselect','Multiselect'),
                                            ('boolean','Boolean'),
                                            ('integer','Integer'),
                                            ('date','Date'),
                                            ('datetime','Datetime'),
                                            ('binary','Binary'),
                                            ('float','Float')],
                                           'Type', required=True),
        'serialized': fields.boolean('Field serialized',
                                     help="If serialized, the field will be stocked in the serialized field: "
                                     "attribute_custom_tmpl or attribute_custom_variant depending on the field based_on"),
        'based_on': fields.selection([('product_template','Product Template'),
                                      ('product_product','Product Variant')],
                                     'Based on', required=True),
        'option_ids': fields.one2many('attribute.option', 'attribute_id', 'Attribute Options'),
        'create_date': fields.datetime('Created date', readonly=True),
        'relation_model_id': fields.many2one('ir.model', 'Model'),
        'domain': fields.char('Domain', size=256),
        }

    def create(self, cr, uid, vals, context=None):
        if vals.get('relation_model_id'):
            relation = self.pool.get('ir.model').read(cr, uid, [vals.get('relation_model_id')], ['model'])[0]['model']
        else:
            relation = 'attribute.option'
        if vals.get('based_on') == 'product_template':
            vals['model_id'] = self.pool.get('ir.model').search(cr, uid, [('model', '=', 'product.template')], context=context)[0]
            serial_name = 'attribute_custom_tmpl'
        else:
            vals['model_id'] = self.pool.get('ir.model').search(cr, uid, [('model', '=', 'product.product')], context=context)[0]
            serial_name = 'attribute_custom_variant'
        if vals.get('serialized'):
            vals['serialization_field_id'] = self.pool.get('ir.model.fields').search(cr, uid, [('name', '=', serial_name)], context=context)[0]
        if vals['attribute_type'] == 'select':
            vals['ttype'] = 'many2one'
            vals['relation'] = relation
        elif vals['attribute_type'] == 'multiselect':
            vals['ttype'] = 'many2many'
            vals['relation'] = relation
            if not vals.get('serialized'):
                raise except_osv(_('Create Error'), _("The field serialized should be ticked for a multiselect field !"))
        else:
            vals['ttype'] = vals['attribute_type']
        vals['state'] = 'manual'
        return super(product_attribute, self).create(cr, uid, vals, context)

    def onchange_field_description(self, cr, uid, ids, field_description, context=None):
        name = 'x_'
        if field_description:
            name = unidecode('x_%s' % field_description.replace(' ', '_').lower())
        return  {'value' : {'name' : name}}

    def onchange_name(self, cr, uid, ids, name, context=None):
        if not name.startswith('x_'):
            name = 'x_%s' % name
        return  {'value' : {'name' : unidecode(name)}}

class attribute_location(Model):
    _name = "attribute.location"
    _description = "Attribute Location"
    _order="sequence"
    _inherits = {'product.attribute': 'attribute_id'}


    def _get_attribute_loc_from_group(self, cr, uid, ids, context=None):
        return self.pool.get('attribute.location').search(cr, uid, [('attribute_group_id', 'in', ids)], context=context)

    _columns = {
        'attribute_id': fields.many2one('product.attribute', 'Product Attribute', required=True, ondelete="cascade"),
        'attribute_set_id': fields.related('attribute_group_id', 'attribute_set_id', type='many2one', relation='attribute.set', string='Attribute Set', readonly=True,
store={
            'attribute.group': (_get_attribute_loc_from_group, ['attribute_set_id'], 10),
        }),
        'attribute_group_id': fields.many2one('attribute.group', 'Attribute Group', required=True),
        'sequence': fields.integer('Sequence'),
        }



class attribute_group(Model):
    _name= "attribute.group"
    _description = "Attribute Group"
    _order="sequence"

    _columns = {
        'name': fields.char('Name', size=128, required=True),
        'attribute_set_id': fields.many2one('attribute.set', 'Attribute Set'),
        'attribute_ids': fields.one2many('attribute.location', 'attribute_group_id', 'Attributes'),
        'sequence': fields.integer('Sequence'),
    }

    def create(self, cr, uid, vals, context=None):
        for attribute in vals['attribute_ids']:
            if vals.get('attribute_set_id') and attribute[2] and not attribute[2].get('attribute_set_id'):
                attribute[2]['attribute_set_id'] = vals['attribute_set_id']
        return super(attribute_group, self).create(cr, uid, vals, context)

class attribute_set(Model):
    _name = "attribute.set"
    _description = "Attribute Set"
    _columns = {
        'name': fields.char('Name', size=128, required=True),
        'attribute_group_ids': fields.one2many('attribute.group', 'attribute_set_id', 'Attribute Groups'),
        }

