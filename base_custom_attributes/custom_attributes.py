# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
#   base_custom_attributes for OpenERP                                        #
#   Copyright (C) 2011 Akretion Benoît GUILLOT <benoit.guillot@akretion.com>  #
#   Copyright (C) 2013 Akretion Raphaël VALYI <raphael.valyi@akretion.com>    #
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
from openerp.osv.orm import setup_modifiers
from tools.translate import _
from lxml import etree

from unidecode import unidecode # Debian package python-unidecode

class attribute_option(Model):
    _name = "attribute.option"
    _description = "Attribute Option"
    _order="sequence"

    _columns = {
        'name': fields.char('Name', size=128, translate=True, required=True),
        'value_ref': fields.reference('Reference', selection=[], size=128),
        'attribute_id': fields.many2one('custom.attribute', 'Product Attribute', required=True),
        'sequence': fields.integer('Sequence'),
    }

    def name_change(self, cr, uid, ids, name, relation_model_id, context=None):
        if relation_model_id:
            warning = {'title': _('Error!'), 'message': _("Use the 'Change Options' button instead to select appropriate model references'")}
            return {"value": {"name": False}, "warning": warning}
        else:
            return True


class attribute_option_wizard(orm.TransientModel):
    _name = "attribute.option.wizard"
    _rec_name = 'attribute_id'

    _columns = {
        'attribute_id': fields.many2one('custom.attribute', 'Product Attribute', required=True),
    }

    _defaults = {
        'attribute_id': lambda self, cr, uid, context: context.get('attribute_id', False)
    }

    def validate(self, cr, uid, ids, context=None):
        return True

    def create(self, cr, uid, vals, context=None):
        attr_obj = self.pool.get("custom.attribute")
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
            attr_obj = self.pool.get("custom.attribute")
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


class custom_attribute(Model):
    _name = "custom.attribute"
    _description = "Product Attribute"
    _inherits = {'ir.model.fields': 'field_id'}

    def _build_attribute_field(self, cr, uid, page, attribute, context=None):
        parent = etree.SubElement(page, 'group')
        kwargs = {'name': "%s" % attribute.name}
        if attribute.ttype == 'many2many':
            parent = etree.SubElement(parent, 'group')
            sep = etree.SubElement(parent, 'separator',
                                    string="%s" % attribute.field_description)
            kwargs['nolabel'] = "1"
        if attribute.ttype in ['many2one', 'many2many']:
            if attribute.relation_model_id:
                if attribute.domain:
                    kwargs['domain'] = attribute.domain
                else:
                    ids = [op.value_ref.id for op in attribute.option_ids]
                    kwargs['domain'] = "[('id', 'in', %s)]" % ids
            else:
                kwargs['domain'] = "[('attribute_id', '=', %s)]" % attribute.attribute_id.id
        field = etree.SubElement(parent, 'field', **kwargs)
        setup_modifiers(field, self.fields_get(cr, uid, attribute.name, context))
        return parent

    def _build_attributes_notebook(self, cr, uid, attribute_group_ids, context=None):
        notebook = etree.Element('notebook', name="attributes_notebook", colspan="4")
        toupdate_fields = []
        grp_obj = self.pool.get('attribute.group')
        for group in grp_obj.browse(cr, uid, attribute_group_ids, context=context):
            page = etree.SubElement(notebook, 'page', string=group.name.capitalize())
            for attribute in group.attribute_ids:
                if attribute.name not in toupdate_fields:
                    toupdate_fields.append(attribute.name)
                    self._build_attribute_field(cr, uid, page, attribute, context=context)
        return notebook, toupdate_fields

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
        'option_ids': fields.one2many('attribute.option', 'attribute_id', 'Attribute Options'),
        'create_date': fields.datetime('Created date', readonly=True),
        'relation_model_id': fields.many2one('ir.model', 'Model'),
        'domain': fields.char('Domain', size=256),
        }

    def create(self, cr, uid, vals, context=None):
        if vals.get('relation_model_id'):
            relation = self.pool.get('ir.model').read(cr, uid,
            [vals.get('relation_model_id')], ['model'])[0]['model']
        else:
            relation = 'attribute.option'
        if vals.get('serialized'):
            field_obj = self.pool.get('ir.model.fields')
            serialized_ids = field_obj.search(cr, uid,
            [('ttype', '=', 'serialized'), ('model_id', '=', vals['model_id']),
            ('name', '=', 'x_custom_json_attrs')], context=context)
            if serialized_ids:
                vals['serialization_field_id'] = serialized_ids[0]
            else:
                f_vals = {
                    'name': 'x_custom_json_attrs',
                    'field_description': 'Serialized JSON Attributes', 
                    'ttype': 'serialized',
                    'model_id': vals['model_id'],
                }
                vals['serialization_field_id'] = field_obj.create(cr, uid, f_vals, {'manual': True})
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
        return super(custom_attribute, self).create(cr, uid, vals, context)

    def onchange_field_description(self, cr, uid, ids, field_description, context=None):
        name = 'x_'
        if field_description:
            name = unidecode('x_%s' % field_description.replace(' ', '_').lower())
        return  {'value' : {'name' : name}}

    def onchange_name(self, cr, uid, ids, name, context=None):
        if not name.startswith('x_'):
            name = 'x_%s' % name
        return  {'value' : {'name' : unidecode(name)}}


class attribute_group(Model):
    _name= "attribute.group"
    _description = "Attribute Group"
    _order="sequence"

    _columns = {
        'name': fields.char('Name', size=128, required=True),
        'sequence': fields.integer('Sequence'),
        'attribute_ids': fields.one2many('attribute.location', 'attribute_group_id', 'Attributes'),
    }

class attribute_location(Model):
    _name = "attribute.location"
    _description = "Attribute Location"
    _order="sequence"
    _inherits = {'custom.attribute': 'attribute_id'}


    def _get_attribute_loc_from_group(self, cr, uid, ids, context=None):
        return self.pool.get('attribute.location').search(cr, uid, [('attribute_group_id', 'in', ids)], context=context)

    _columns = {
        'attribute_id': fields.many2one('custom.attribute', 'Product Attribute', required=True, ondelete="cascade"),
        'attribute_group_id': fields.many2one('attribute.group', 'Attribute Group', required=True),
        'sequence': fields.integer('Sequence'),
        }
