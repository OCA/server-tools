# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
#   base_attribute.attributes for OpenERP                                        #
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

from openerp.osv import orm, fields
from openerp.osv.osv import except_osv
from openerp.tools.translate import _
from lxml import etree
from unidecode import unidecode # Debian package python-unidecode


class attribute_option(orm.Model):
    _name = "attribute.option"
    _description = "Attribute Option"
    _order="sequence"

    _columns = {
        'name': fields.char('Name', size=128, translate=True, required=True),
        'value_ref': fields.reference('Reference', selection=[], size=128),
        'attribute_id': fields.many2one('attribute.attribute', 'Product Attribute', required=True),
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
        'attribute_id': fields.many2one('attribute.attribute', 'Product Attribute', required=True),
    }

    _defaults = {
        'attribute_id': lambda self, cr, uid, context: context.get('attribute_id', False)
    }

    def validate(self, cr, uid, ids, context=None):
        return True

    def create(self, cr, uid, vals, context=None):
        attr_obj = self.pool.get("attribute.attribute")
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
        if view_type == 'form' and context and context.get("attribute_id"):
            attr_obj = self.pool.get("attribute.attribute")
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


class attribute_attribute(orm.Model):
    _name = "attribute.attribute"
    _description = "Attribute"
    _inherits = {'ir.model.fields': 'field_id'}

    def _build_attribute_field(self, cr, uid, page, attribute, context=None):
        parent = etree.SubElement(page, 'group', colspan="2", col="4")
        kwargs = {'name': "%s" % attribute.name}
        if attribute.ttype in ['many2many', 'text']:
            parent = etree.SubElement(parent, 'group', colspan="2", col="4")
            sep = etree.SubElement(parent,
                                   'separator',
                                    string="%s" % attribute.field_description,
                                    colspan="4")  
        
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
        orm.setup_modifiers(field, self.fields_get(cr, uid, attribute.name, context))
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

        if vals['attribute_type'] == 'select':
            vals['ttype'] = 'many2one'
            vals['relation'] = relation
        elif vals['attribute_type'] == 'multiselect':
            vals['ttype'] = 'many2many'
            vals['relation'] = relation
            vals['serialized'] = True
        else:
            vals['ttype'] = vals['attribute_type']

        if vals.get('serialized'):
            field_obj = self.pool.get('ir.model.fields')
            serialized_ids = field_obj.search(cr, uid,
            [('ttype', '=', 'serialized'), ('model_id', '=', vals['model_id']),
            ('name', '=', 'x_custom_json_attrs')], context=context)
            if serialized_ids:
                vals['serialization_field_id'] = serialized_ids[0]
            else:
                f_vals = {
                    'name': u'x_custom_json_attrs',
                    'field_description': u'Serialized JSON Attributes', 
                    'ttype': 'serialized',
                    'model_id': vals['model_id'],
                }
                vals['serialization_field_id'] = field_obj.create(cr, uid, f_vals, {'manual': True})
        vals['state'] = 'manual'
        return super(attribute_attribute, self).create(cr, uid, vals, context)

    def onchange_field_description(self, cr, uid, ids, field_description, context=None):
        name = u'x_'
        if field_description:
            name = unidecode(u'x_%s' % field_description.replace(' ', '_').lower())
        return  {'value' : {'name' : name}}

    def onchange_name(self, cr, uid, ids, name, context=None):
        res = {}
        if not name.startswith('x_'):
            name = u'x_%s' % name
        else:
            name = u'%s' % name
        res = {'value' : {'name' : unidecode(name)}}

        #FILTER ON MODEL
        model_domain = []
        model_name = context.get('force_model')
        if not model_name:
            model_id = context.get('default_model_id')
            if model_id:
                model = self.pool['ir.model'].browse(cr, uid, model_id, context=context)
                model_name = model.model
        if model_name:
            model_obj = self.pool[model_name]
            allowed_model = [x for x in model_obj._inherits] + [model_name]
            res['domain'] = {'model_id': [['model', 'in', allowed_model]]}

        return res

    def _get_default_model(self, cr, uid, context=None):
        if context and context.get('force_model'):
            model_id = self.pool['ir.model'].search(cr, uid, [
                    ['model', '=', context['force_model']]
                    ], context=context)
            if model_id:
                return model_id[0]
        return None

    _defaults = {
        'model_id': _get_default_model
    }


class attribute_group(orm.Model):
    _name= "attribute.group"
    _description = "Attribute Group"
    _order="sequence"

    _columns = {
        'name': fields.char('Name', size=128, required=True),
        'sequence': fields.integer('Sequence'),
        'attribute_set_id': fields.many2one('attribute.set', 'Attribute Set'),
        'attribute_ids': fields.one2many('attribute.location', 'attribute_group_id', 'Attributes'),
        'model_id': fields.many2one('ir.model', 'Model', required=True),
    }

    def create(self, cr, uid, vals, context=None):
        for attribute in vals['attribute_ids']:
            if vals.get('attribute_set_id') and attribute[2] and not attribute[2].get('attribute_set_id'):
                attribute[2]['attribute_set_id'] = vals['attribute_set_id']
        return super(attribute_group, self).create(cr, uid, vals, context)

    def _get_default_model(self, cr, uid, context=None):
        if context and context.get('force_model'):
            model_id = self.pool['ir.model'].search(cr, uid, [
                    ['model', '=', context['force_model']]
                    ], context=context)
            if model_id:
                return model_id[0]
        return None

    _defaults = {
        'model_id': _get_default_model
    }


class attribute_set(orm.Model):
    _name = "attribute.set"
    _description = "Attribute Set"
    _columns = {
        'name': fields.char('Name', size=128, required=True),
        'attribute_group_ids': fields.one2many('attribute.group', 'attribute_set_id', 'Attribute Groups'),
        'model_id': fields.many2one('ir.model', 'Model', required=True),
        }

    def _get_default_model(self, cr, uid, context=None):
        if context and context.get('force_model'):
            model_id = self.pool['ir.model'].search(cr, uid, [
                    ['model', '=', context['force_model']]
                    ], context=context)
            if model_id:
                return model_id[0]
        return None

    _defaults = {
        'model_id': _get_default_model
    }

class attribute_location(orm.Model):
    _name = "attribute.location"
    _description = "Attribute Location"
    _order="sequence"
    _inherits = {'attribute.attribute': 'attribute_id'}


    def _get_attribute_loc_from_group(self, cr, uid, ids, context=None):
        return self.pool.get('attribute.location').search(cr, uid, [('attribute_group_id', 'in', ids)], context=context)

    _columns = {
        'attribute_id': fields.many2one('attribute.attribute', 'Product Attribute', required=True, ondelete="cascade"),
        'attribute_set_id': fields.related('attribute_group_id', 'attribute_set_id', type='many2one', relation='attribute.set', string='Attribute Set', readonly=True,
store={
            'attribute.group': (_get_attribute_loc_from_group, ['attribute_set_id'], 10),
        }),
        'attribute_group_id': fields.many2one('attribute.group', 'Attribute Group', required=True),
        'sequence': fields.integer('Sequence'),
        }
