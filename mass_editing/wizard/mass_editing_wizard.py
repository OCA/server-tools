# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Serpent Consulting Services (<http://www.serpentcs.com>)
#    Copyright (C) 2010-Today OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from osv import osv
from osv import fields
from lxml import etree
import tools

class mass_editing_wizard(osv.osv_memory):
    _name = 'mass.editing.wizard'

    _columns = {
        'serpent_image': fields.binary('Image'),
    }

    _defaults = {
        'serpent_image': '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',
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        result = super(mass_editing_wizard, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar,submenu)
        if context.get('mass_editing_object'):
            mass_object = self.pool.get('mass.object') 
            editing_data = mass_object.browse(cr, uid, context.get('mass_editing_object'), context)
            all_fields = {}
            xml_form = etree.Element('form', {'string': tools.ustr(editing_data.name)})
            xml_group = etree.SubElement(xml_form, 'group', {'colspan': '4'})
            etree.SubElement(xml_group, 'field', {'name': 'serpent_image', 'nolabel': '1','colspan': '1', 'modifiers': '{"readonly": true}', 'widget':'image'})
            etree.SubElement(xml_group, 'label', {'string': '','colspan': '2'})
            all_fields['serpent_image'] = {'type':'binary', 'string':''}
            xml_group = etree.SubElement(xml_form, 'group', {'colspan': '4'})
            model_obj = self.pool.get(context.get('active_model'))
            for field in editing_data.field_ids:
                if field.ttype == "many2many":
                    field_info = model_obj.fields_get(cr, uid, [field.name], context)
                    all_fields[field.name] = field_info[field.name]
                    all_fields["selection_"+field.name] = {'type':'selection', 'string': field_info[field.name]['string'],'selection':[('set','Set'),('remove_m2m','Remove'),('add','Add')]}
                    xml_group = etree.SubElement(xml_group, 'group', {'colspan': '4'})
                    etree.SubElement(xml_group, 'separator', {'string': field_info[field.name]['string'],'colspan': '2'})
                    etree.SubElement(xml_group, 'field', {'name': "selection_"+field.name,'colspan': '2','nolabel':'1'})
                    etree.SubElement(xml_group, 'field', {'name': field.name, 'colspan':'4', 'nolabel':'1', 'attrs':"{'invisible':[('selection_"+field.name+"','=','remove_m2m')]}"})
                elif field.ttype == "many2one":
                    field_info = model_obj.fields_get(cr, uid, [field.name], context)
                    if field_info:
                        all_fields["selection_"+field.name] = {'type':'selection', 'string': field_info[field.name]['string'],'selection':[('set','Set'),('remove','Remove')]}
                        all_fields[field.name] = {'type':field.ttype, 'string': field.field_description, 'relation': field.relation}
                        etree.SubElement(xml_group, 'field', {'name': "selection_"+field.name, 'colspan':'2'})
                        etree.SubElement(xml_group, 'field', {'name': field.name,'nolabel':'1','colspan':'2', 'attrs':"{'invisible':[('selection_"+field.name+"','=','remove')]}"})
                elif field.ttype == "char":
                    field_info = model_obj.fields_get(cr, uid, [field.name], context)
                    all_fields["selection_"+field.name] = {'type':'selection', 'string': field_info[field.name]['string'],'selection':[('set','Set'),('remove','Remove')]}
                    all_fields[field.name] = {'type':field.ttype, 'string': field.field_description, 'size': field.size or 256}
                    etree.SubElement(xml_group, 'field', {'name': "selection_"+field.name,'colspan':'2', 'colspan':'2'})
                    etree.SubElement(xml_group, 'field', {'name': field.name,'nolabel':'1', 'attrs':"{'invisible':[('selection_"+field.name+"','=','remove')]}", 'colspan':'2'})
                elif field.ttype == 'selection':
                    field_info = model_obj.fields_get(cr, uid, [field.name], context)
                    all_fields["selection_"+field.name] = {'type':'selection', 'string': field_info[field.name]['string'],'selection':[('set','Set'),('remove','Remove')]}
                    field_info = model_obj.fields_get(cr, uid, [field.name], context)
                    etree.SubElement(xml_group, 'field', {'name': "selection_"+field.name, 'colspan':'2'})
                    etree.SubElement(xml_group, 'field', {'name': field.name,'nolabel':'1','colspan':'2', 'attrs':"{'invisible':[('selection_"+field.name+"','=','remove')]}"})
                    all_fields[field.name] = {'type':field.ttype, 'string': field.field_description, 'selection': field_info[field.name]['selection']}
                else:
                    field_info = model_obj.fields_get(cr, uid, [field.name], context)
                    all_fields[field.name] = {'type':field.ttype, 'string': field.field_description}
                    all_fields["selection_"+field.name] = {'type':'selection', 'string': field_info[field.name]['string'],'selection':[('set','Set'),('remove','Remove')]}
                    if field.ttype == 'text':
                        xml_group = etree.SubElement(xml_group, 'group', {'colspan': '6'})
                        etree.SubElement(xml_group, 'separator', {'string': all_fields[field.name]['string'],'colspan': '2'})
                        etree.SubElement(xml_group, 'field', {'name': "selection_"+field.name,'colspan': '2','nolabel':'1'})
                        etree.SubElement(xml_group, 'field', {'name': field.name, 'colspan':'4', 'nolabel':'1', 'attrs':"{'invisible':[('selection_"+field.name+"','=','remove')]}"})
                    else:
                        all_fields["selection_"+field.name] = {'type':'selection', 'string': field_info[field.name]['string'],'selection':[('set','Set'),('remove','Remove')]}
                        etree.SubElement(xml_group, 'field', {'name': "selection_"+field.name, 'colspan': '2',})
                        etree.SubElement(xml_group, 'field', {'name': field.name,'nolabel':'1', 'attrs':"{'invisible':[('selection_"+field.name+"','=','remove')]}",'colspan': '2',})

            etree.SubElement(xml_form, 'separator', {'string' : '','colspan': '6'})
            xml_group3 = etree.SubElement(xml_form, 'group', {'col': '2', 'colspan': '4'})
            etree.SubElement(xml_group3, 'button', {'string' :'Close','icon': "gtk-close", 'special' :'cancel'})
            etree.SubElement(xml_group3, 'button', {'string' :'Apply','icon': "gtk-execute", 'type' :'object','name':"action_apply"})

            root = xml_form.getroottree()
            result['arch'] = etree.tostring(root)
            result['fields'] = all_fields
        return result

    def create(self, cr, uid, vals, context=None):
        if context.get('active_model') and context.get('active_ids'):
            model_obj = self.pool.get(context.get('active_model'))
            dict = {}
            for key ,val in vals.items():
                if key.startswith('selection_'):
                    split_key= key.split('_',1)[1]
                    if val == 'set':
                        dict.update({split_key: vals.get(split_key, False)})
                    elif val == 'remove':
                        dict.update({split_key: False})
                    elif val == 'remove_m2m':
                        dict.update({split_key: [(5,0,[])]})
                    elif val == 'add':
                        m2m_list = []
                        for m2m_id in vals.get(split_key, False)[0][2]:
                            m2m_list.append((4, m2m_id))
                        dict.update({split_key: m2m_list})
            if dict:
                model_obj.write(cr, uid, context.get('active_ids'), dict, context)
        result = super(mass_editing_wizard, self).create(cr, uid, {}, context)
        return result

    def action_apply(self, cr, uid, ids, context=None):
        return  {'type': 'ir.actions.act_window_close'}

mass_editing_wizard()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
