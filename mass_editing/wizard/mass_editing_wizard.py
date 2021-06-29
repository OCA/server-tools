# -*- coding: utf-8 -*-
# © 2016 Serpent Consulting Services Pvt. Ltd. (support@serpentcs.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import etree

import odoo.tools as tools
from odoo import api, models


class MassEditingWizard(models.TransientModel):
    _name = 'mass.editing.wizard'

    @api.model
    def _get_field_options(self, field):
        return {"name": field.name, "nolabel": "1", "colspan": "4"}

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        result =\
            super(MassEditingWizard, self).fields_view_get(view_id=view_id,
                                                           view_type=view_type,
                                                           toolbar=toolbar,
                                                           submenu=submenu)
        context = self._context
        if context.get('mass_editing_object'):
            mass_obj = self.env['mass.editing']
            editing_data = mass_obj.browse(context.get('mass_editing_object'))
            all_fields = {}
            xml_form = etree.Element('form', {
                'string': tools.ustr(editing_data.name)
            })
            xml_group = etree.SubElement(xml_form, 'group', {
                'colspan': '6',
                'col': '6',
            })
            etree.SubElement(xml_group, 'label', {
                'string': '',
                'colspan': '2',
            })
            xml_group = etree.SubElement(xml_form, 'group', {
                'colspan': '6',
                'col': '6',
            })
            model_obj = self.env[context.get('active_model')]
            field_info = model_obj.fields_get()
            for line in editing_data.line_ids:
                field = line.field_id
                all_fields[field.name] = field_info[field.name]
                if field.ttype == "many2many":
                    all_fields["selection__" + field.name] = {
                        'type': 'selection',
                        'string': field_info[field.name]['string'],
                        'selection': [('set', 'Set'),
                                      ('remove_m2m', 'Remove'),
                                      ('add', 'Add')]
                    }
                else:
                    all_fields["selection__" + field.name] = {
                        'type': 'selection',
                        'string': field_info[field.name]['string'],
                        'selection': [('set', 'Set'),
                                      ('remove_m2m', 'Remove')]
                    }
                etree.SubElement(
                    xml_group,
                    "field",
                    {"name": "selection__" + field.name, "colspan": "2"},
                )
                field_vals = self._get_field_options(field)
                if line.widget_option:
                    field_vals["widget"] = line.widget_option
                if not line.apply_domain and "domain" in field_info[field.name]:
                    field_vals["domain"] = "[]"
                etree.SubElement(xml_group, "field", field_vals)

            # Patch fields with required extra data
            for field in all_fields.values():
                field.setdefault("views", {})
            etree.SubElement(xml_form, 'separator', {
                'string': '',
                'colspan': '6',
                'col': '6',
            })
            xml_group3 = etree.SubElement(xml_form, 'footer', {})
            etree.SubElement(xml_group3, 'button', {
                'string': 'Apply',
                'class': 'btn-primary',
                'type': 'object',
                'name': 'action_apply',
            })
            etree.SubElement(xml_group3, 'button', {
                'string': 'Close',
                'class': 'btn-default',
                'special': 'cancel',
            })
            root = xml_form.getroottree()
            result['arch'] = etree.tostring(root)
            result['fields'] = all_fields
        return result

    @api.model
    def create(self, vals):
        if (self._context.get('active_model') and
                self._context.get('active_ids')):
            model_obj = self.env[self._context.get('active_model')]
            model_field_obj = self.env['ir.model.fields']
            translation_obj = self.env['ir.translation']
            values = {}
            for key, val in vals.items():
                if key.startswith('selection_'):
                    split_key = key.split('__', 1)[1]
                    if val == 'set':
                        values.update({split_key: vals.get(split_key, False)})
                    elif val == 'remove':
                        values.update({split_key: False})
                        # If field to remove is translatable,
                        # its translations have to be removed
                        model_field = model_field_obj.search([
                            ('model', '=', self._context.get('active_model')),
                            ('name', '=', split_key)])
                        if model_field and model_field.translate:
                            translation_ids = translation_obj.search([
                                ('res_id', 'in', self._context.get(
                                    'active_ids')),
                                ('type', '=', 'model'),
                                ('name', '=', u"{0},{1}".format(
                                    self._context.get('active_model'),
                                    split_key))])
                            translation_ids.unlink()

                    elif val == 'remove_m2m':
                        values.update({split_key: [(5, 0, [])]})
                    elif val == 'add':
                        m2m_list = []
                        for m2m_id in vals.get(split_key, False)[0][2]:
                            m2m_list.append((4, m2m_id))
                        values.update({split_key: m2m_list})
            if values:
                model_obj.browse(self._context.get('active_ids')).write(values)
        return super(MassEditingWizard, self).create({})

    @api.multi
    def action_apply(self):
        return {'type': 'ir.actions.act_window_close'}

    def read(self, fields, load='_classic_read'):
        """ Without this call, dynamic fields build by fields_view_get()
            generate a log warning, i.e.:
            odoo.models:mass.editing.wizard.read() with unknown field 'myfield'
            odoo.models:mass.editing.wizard.read()
                with unknown field 'selection__myfield'
        """
        real_fields = fields
        if fields:
            # We remove fields which are not in _fields
            real_fields = [x for x in fields if x in self._fields]
        return super(MassEditingWizard, self).read(real_fields, load=load)
