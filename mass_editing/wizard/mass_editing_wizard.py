# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C):
#        2012-Today Serpent Consulting Services (<http://www.serpentcs.com>)
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

from openerp.osv import orm
import openerp.tools as tools
from lxml import etree


class mass_editing_wizard(orm.TransientModel):
    _name = 'mass.editing.wizard'

    _columns = {
    }

    def fields_view_get(
            self, cr, uid, view_id=None, view_type='form', context=None,
            toolbar=False, submenu=False):
        result = super(mass_editing_wizard, self).fields_view_get(
            cr, uid, view_id, view_type, context, toolbar, submenu)
        if context.get('mass_editing_object'):
            mass_object = self.pool.get('mass.object')
            editing_data = mass_object.browse(
                cr, uid, context.get('mass_editing_object'), context)
            all_fields = {}
            xml_form = etree.Element('form', {
                'string': tools.ustr(editing_data.name), 'version': '7.0'})
            xml_group = etree.SubElement(xml_form, 'group', {'colspan': '4'})
            etree.SubElement(xml_group, 'label', {
                'string': '', 'colspan': '2'})
            xml_group = etree.SubElement(xml_form, 'group', {'colspan': '4'})
            model_obj = self.pool.get(context.get('active_model'))
            field_info = model_obj.fields_get(cr, uid, [], context)
            for field in editing_data.field_ids:
                if field.ttype == "many2many":
                    all_fields[field.name] = field_info[field.name]
                    all_fields["selection__" + field.name] = {
                        'type': 'selection',
                        'string': field_info[field.name]['string'],
                        'selection': [
                            ('set', 'Set'), ('remove_m2m', 'Remove'),
                            ('add', 'Add')]}
                    xml_group = etree.SubElement(xml_group, 'group', {
                        'colspan': '4'})
                    etree.SubElement(xml_group, 'separator', {
                        'string': field_info[field.name]['string'],
                        'colspan': '2'})
                    etree.SubElement(xml_group, 'field', {
                        'name': "selection__" + field.name,
                        'colspan': '2', 'nolabel': '1'})
                    etree.SubElement(xml_group, 'field', {
                        'name': field.name, 'colspan': '4', 'nolabel': '1',
                        'attrs': (
                            "{'invisible':[('selection__" +
                            field.name + "','=','remove_m2m')]}")})
                elif field.ttype == "one2many":
                    all_fields["selection__" + field.name] = {
                        'type': 'selection',
                        'string': field_info[field.name]['string'],
                        'selection': [('set', 'Set'), ('remove', 'Remove')]}
                    all_fields[field.name] = {
                        'type': field.ttype, 'string': field.field_description,
                        'relation': field.relation}
                    etree.SubElement(xml_group, 'field', {
                        'name': "selection__" + field.name, 'colspan': '2'})
                    etree.SubElement(xml_group, 'field', {
                        'name': field.name, 'colspan': '4', 'nolabel': '1',
                        'attrs': (
                            "{'invisible':[('selection__" +
                            field.name + "','=','remove_o2m')]}")})
                elif field.ttype == "many2one":
                    all_fields["selection__" + field.name] = {
                        'type': 'selection',
                        'string': field_info[field.name]['string'],
                        'selection': [('set', 'Set'), ('remove', 'Remove')]}
                    all_fields[field.name] = {
                        'type': field.ttype, 'string': field.field_description,
                        'relation': field.relation}
                    etree.SubElement(xml_group, 'field', {
                        'name': "selection__" + field.name, 'colspan': '2'})
                    etree.SubElement(xml_group, 'field', {
                        'name': field.name, 'nolabel': '1', 'colspan': '2',
                        'attrs': (
                            "{'invisible':[('selection__" +
                            field.name + "','=','remove')]}")})
                elif field.ttype == "char":
                    all_fields["selection__" + field.name] = {
                        'type': 'selection',
                        'string': field_info[field.name]['string'],
                        'selection': [('set', 'Set'), ('remove', 'Remove')]}
                    all_fields[field.name] = {
                        'type': field.ttype, 'string': field.field_description,
                        'size': field.size or 256}
                    etree.SubElement(xml_group, 'field', {
                        'name': "selection__" + field.name,
                        'colspan': '2'})
                    etree.SubElement(xml_group, 'field', {
                        'name': field.name, 'nolabel': '1',
                        'attrs': (
                            "{'invisible':[('selection__" +
                            field.name + "','=','remove')]}"),
                        'colspan': '2'})
                elif field.ttype == 'selection':
                    all_fields["selection__" + field.name] = {
                        'type': 'selection',
                        'string': field_info[field.name]['string'],
                        'selection': [('set', 'Set'), ('remove', 'Remove')]}
                    etree.SubElement(xml_group, 'field', {
                        'name': "selection__" + field.name, 'colspan': '2'})
                    etree.SubElement(xml_group, 'field', {
                        'name': field.name, 'nolabel': '1', 'colspan': '2',
                        'attrs': (
                            "{'invisible':[('selection__" +
                            field.name + "','=','remove')]}")})
                    all_fields[field.name] = {
                        'type': field.ttype,
                        'string': field.field_description,
                        'selection': field_info[field.name]['selection']}
                else:
                    all_fields[field.name] = {
                        'type': field.ttype, 'string': field.field_description}
                    all_fields["selection__" + field.name] = {
                        'type': 'selection',
                        'string': field_info[field.name]['string'],
                        'selection': [('set', 'Set'), ('remove', 'Remove')]}
                    if field.ttype == 'text':
                        xml_group = etree.SubElement(xml_group, 'group', {
                            'colspan': '6'})
                        etree.SubElement(xml_group, 'separator', {
                            'string': all_fields[field.name]['string'],
                            'colspan': '2'})
                        etree.SubElement(xml_group, 'field', {
                            'name': "selection__" + field.name,
                            'colspan': '2', 'nolabel': '1'})
                        etree.SubElement(xml_group, 'field', {
                            'name': field.name, 'colspan': '4', 'nolabel': '1',
                            'attrs': (
                                "{'invisible':[('selection__" +
                                field.name + "','=','remove')]}")})
                    else:
                        all_fields["selection__" + field.name] = {
                            'type': 'selection',
                            'string': field_info[field.name]['string'],
                            'selection': [(
                                'set', 'Set'), ('remove', 'Remove')]}
                        etree.SubElement(xml_group, 'field', {
                            'name': "selection__" + field.name,
                            'colspan': '2', })
                        etree.SubElement(xml_group, 'field', {
                            'name': field.name, 'nolabel': '1',
                            'attrs': (
                                "{'invisible':[('selection__" +
                                field.name + "','=','remove')]}"),
                            'colspan': '2', })
            etree.SubElement(
                xml_form, 'separator', {'string': '', 'colspan': '4'})
            xml_group3 = etree.SubElement(xml_form, 'footer', {})
            etree.SubElement(xml_group3, 'button', {
                'string': 'Close', 'icon': "gtk-close", 'special': 'cancel'})
            etree.SubElement(xml_group3, 'button', {
                'string': 'Apply', 'icon': "gtk-execute",
                'type': 'object', 'name': "action_apply"})
            root = xml_form.getroottree()
            result['arch'] = etree.tostring(root)
            result['fields'] = all_fields
        return result

    def create(self, cr, uid, vals, context=None):
        if context.get('active_model') and context.get('active_ids'):
            model_obj = self.pool.get(context.get('active_model'))
            dict = {}
            for key, val in vals.items():
                if key.startswith('selection__'):
                    split_key = key.split('__', 1)[1]
                    if val == 'set':
                        dict.update({split_key: vals.get(split_key, False)})
                    elif val == 'remove':
                        dict.update({split_key: False})
                    elif val == 'remove_m2m':
                        dict.update({split_key: [
                            (3, id) for id in vals.get(
                                split_key, False)[0][2]]})
                    elif val == 'add':
                        m2m_list = []
                        for m2m_id in vals.get(split_key, False)[0][2]:
                            m2m_list.append((4, m2m_id))
                        dict.update({split_key: m2m_list})
            if dict:
                model_obj.write(
                    cr, uid, context.get('active_ids'), dict, context)
        result = super(mass_editing_wizard, self).create(cr, uid, {}, context)
        return result

    def action_apply(self, cr, uid, ids, context=None):
        return {'type': 'ir.actions.act_window_close'}
