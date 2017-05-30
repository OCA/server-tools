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


class MassEditingWizard(orm.TransientModel):
    _name = 'mass.editing.wizard'

    def fields_view_get(
            self, cr, uid, view_id=None, view_type='form', context=None,
            toolbar=False, submenu=False):
        result = super(MassEditingWizard, self).fields_view_get(
            cr, uid, view_id, view_type, context, toolbar, submenu)
        if context.get('mass_editing_object'):
            mass_object = self.pool['mass.object']
            editing_data = mass_object.browse(
                cr, uid, context.get('mass_editing_object'), context)
            all_fields = {}
            xml_form = etree.Element('form', {
                'string': tools.ustr(editing_data.name), 'version': '7.0'})
            xml_group = etree.SubElement(xml_form, 'group', {'colspan': '4'})
            etree.SubElement(xml_group, 'label', {
                'string': '', 'colspan': '2'})
            xml_group = etree.SubElement(xml_form, 'group', {'colspan': '4',
                                                             'col': '4'})
            model_obj = self.pool[context.get('active_model')]
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
                        'colspan': '2',
                        })
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
                'string': 'Apply', 'icon': "gtk-execute",
                'type': 'object', 'name': "action_apply",
                'class': "oe_highlight"})
            etree.SubElement(xml_group3, 'button', {
                'string': 'Close', 'icon': "gtk-close", 'special': 'cancel'})
            root = xml_form.getroottree()
            result['arch'] = etree.tostring(root)
            result['fields'] = all_fields
        return result

    def read(self, cr, uid, ids, fields, context=None):
        """ Without this call, dynamic fields defined in fields_view_get()
            generate a log warning, i.e.:

            openerp.models: mass.editing.wizard.read()
                with unknown field 'myfield'
            openerp.models: mass.editing.wizard.read()
                with unknown field 'selection__myfield'
        """
        # We remove fields which are not in _columns
        real_fields = [x for x in fields if x in self._columns]
        return super(MassEditingWizard, self).read(
            cr, uid, ids, real_fields, context=context)

    def create(self, cr, uid, vals, context=None):
        if context.get('active_model') and context.get('active_ids'):
            model_obj = self.pool.get(context.get('active_model'))
            model_field_obj = self.pool.get('ir.model.fields')
            translation_obj = self.pool.get('ir.translation')
            dict = {}
            for key, val in vals.items():
                if key.startswith('selection__'):
                    split_key = key.split('__', 1)[1]
                    if val == 'set':
                        dict.update({split_key: vals.get(split_key, False)})
                    elif val == 'remove':
                        dict.update({split_key: False})
                        # If field to remove is translatable, its translations have to be removed
                        model_field_id = model_field_obj.search(cr, uid, [('model', '=', context.get('active_model')),
                                                                          ('name', '=', split_key)])
                        if model_field_id and \
                                model_field_obj.browse(cr, uid, model_field_id, context=context).translate:
                            translation_ids = translation_obj.search(cr, uid, [
                                                                        ('res_id', 'in', context.get('active_ids')),
                                                                        ('type', '=', 'model'),
                                                                        ('name', '=', u"{0},{1}".format(
                                                                            context.get('active_model'), split_key))])
                            translation_obj.unlink(cr, uid, translation_ids, context=context)

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
        result = super(MassEditingWizard, self).create(cr, uid, {}, context)
        return result

    def action_apply(self, cr, uid, ids, context=None):
        return {'type': 'ir.actions.act_window_close'}
