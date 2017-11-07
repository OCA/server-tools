# -*- coding: utf-8 -*-
# © 2016 Serpent Consulting Services Pvt. Ltd. (support@serpentcs.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
from lxml import etree

from odoo import tools
from odoo import models, api


class MassEditingWizard(models.TransientModel):
    _name = 'mass.editing.wizard'

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
            mass_obj = self.env['mass.object']
            editing_data = mass_obj.browse(context.get('mass_editing_object'))
            all_fields = {}
            xml_form = etree.Element('form', {
                'string': tools.ustr(editing_data.name)
            })
            xml_group = etree.SubElement(xml_form, 'group', {
                'colspan': '6',
                'col': '6',
            })
            model_obj = self.env[context.get('active_model')]
            field_info = model_obj.fields_get()
            for field in editing_data.field_ids:
                if field.ttype == "many2many":
                    all_fields[field.name] = field_info[field.name]
                    all_fields["selection__" + field.name] = {
                        'type': 'selection',
                        'string': field_info[field.name]['string'],
                        'selection': [('set', 'Set'),
                                      ('remove_m2m', 'Remove Specific'),
                                      ('remove_m2m_all', 'Remove All'),
                                      ('add', 'Add')]
                    }
                    xml_group = etree.SubElement(xml_group, 'group', {
                        'colspan': '6',
                        'col': '6',
                    })
                    etree.SubElement(xml_group, 'separator', {
                        'string': field_info[field.name]['string'],
                        'colspan': '6',
                    })
                    etree.SubElement(xml_group, 'field', {
                        'name': "selection__" + field.name,
                        'colspan': '6',
                        'nolabel': '1'
                    })
                    etree.SubElement(xml_group, 'field', {
                        'name': field.name,
                        'colspan': '6',
                        'nolabel': '1',
                        'attrs': "{'invisible': [('selection__" +
                        field.name + "', '=', 'remove_m2m')]}",
                    })
                elif field.ttype == "one2many":
                    all_fields["selection__" + field.name] = {
                        'type': 'selection',
                        'string': field_info[field.name]['string'],
                        'selection': [('set', 'Set'),
                                      ('remove_o2m', 'Remove')],
                    }
                    all_fields[field.name] = {
                        'type': field.ttype,
                        'string': field.field_description,
                        'relation': field.relation,
                    }
                    xml_group = etree.SubElement(xml_group, 'group', {
                        'colspan': '6',
                        'col': '6',
                    })
                    etree.SubElement(xml_group, 'separator', {
                        'string': field_info[field.name]['string'],
                        'colspan': '6',
                    })
                    etree.SubElement(xml_group, 'field', {
                        'name': "selection__" + field.name,
                        'colspan': '6',
                        'nolabel': '1'
                    })
                    etree.SubElement(xml_group, 'field', {
                        'name': field.name,
                        'colspan': '6',
                        'nolabel': '1',
                        'attrs': "{'invisible':[('selection__" +
                        field.name + "', '=', 'remove_o2m')]}",
                    })
                elif field.ttype == "many2one":
                    all_fields["selection__" + field.name] = {
                        'type': 'selection',
                        'string': field_info[field.name]['string'],
                        'selection': [('set', 'Set'), ('remove', 'Remove')],
                    }
                    all_fields[field.name] = {
                        'type': field.ttype,
                        'string': field.field_description,
                        'relation': field.relation,
                    }
                    etree.SubElement(xml_group, 'field', {
                        'name': "selection__" + field.name,
                        'colspan': '2',
                    })
                    etree.SubElement(xml_group, 'field', {
                        'name': field.name,
                        'nolabel': '1',
                        'colspan': '4',
                        'attrs': "{'invisible':[('selection__" +
                        field.name + "', '=', 'remove')]}",
                    })
                elif field.ttype == "float":
                    all_fields["selection__" + field.name] = {
                        'type': 'selection',
                        'string': field_info[field.name]['string'],
                        'selection': [('set', 'Set'),
                                      ('val_add', '+'),
                                      ('val_sub', '-'),
                                      ('val_mul', '*'),
                                      ('val_div', '/'),
                                      ('remove', 'Remove')],
                    }
                    all_fields["set_selection_" + field.name] = {
                        'type': 'selection',
                        'string': 'Set calculation',
                        'selection': [('set_fix', 'Fixed'),
                                      ('set_per', 'Percentage')],
                    }
                    all_fields[field.name] = {
                        'type': field.ttype,
                        'string': field.field_description,
                        'relation': field.relation,
                    }
                    etree.SubElement(xml_group, 'field', {
                        'name': "selection__" + field.name,
                        'colspan': '2',
                    })
                    etree.SubElement(xml_group, 'field', {
                        'name': "set_selection_" + field.name,
                        'nolabel': '1',
                        'colspan': '1',
                        'attrs': "{'invisible': [('selection__" +
                        field.name + "', 'in', ('remove', 'set')]}",
                    })
                    etree.SubElement(xml_group, 'field', {
                        'name': field.name,
                        'nolabel': '1',
                        'colspan': '3',
                        'attrs': "{'invisible':[('selection__" +
                        field.name + "', '=', 'remove')]}",
                    })
                elif field.ttype == "char":
                    all_fields["selection__" + field.name] = {
                        'type': 'selection',
                        'string': field_info[field.name]['string'],
                        'selection': [('set', 'Set'), ('remove', 'Remove')],
                    }
                    all_fields[field.name] = {
                        'type': field.ttype,
                        'string': field.field_description,
                        'size': field.size or 256,
                    }
                    etree.SubElement(xml_group, 'field', {
                        'name': "selection__" + field.name,
                        'colspan': '2',
                    })
                    etree.SubElement(xml_group, 'field', {
                        'name': field.name,
                        'nolabel': '1',
                        'attrs': "{'invisible':[('selection__" +
                        field.name + "','=','remove')]}",
                        'colspan': '4',
                    })
                elif field.ttype == 'selection':
                    all_fields["selection__" + field.name] = {
                        'type': 'selection',
                        'string': field_info[field.name]['string'],
                        'selection': [('set', 'Set'), ('remove', 'Remove')]
                    }
                    etree.SubElement(xml_group, 'field', {
                        'name': "selection__" + field.name,
                        'colspan': '2',
                    })
                    etree.SubElement(xml_group, 'field', {
                        'name': field.name,
                        'nolabel': '1',
                        'colspan': '4',
                        'attrs': "{'invisible':[('selection__" +
                        field.name + "', '=', 'remove')]}",
                    })
                    all_fields[field.name] = {
                        'type': field.ttype,
                        'string': field.field_description,
                        'selection': field_info[field.name]['selection'],
                    }
                else:
                    all_fields[field.name] = {
                        'type': field.ttype,
                        'string': field.field_description,
                    }
                    all_fields["selection__" + field.name] = {
                        'type': 'selection',
                        'string': field_info[field.name]['string'],
                        'selection': [('set', 'Set'), ('remove', 'Remove')]
                    }
                    if field.ttype == 'text':
                        xml_group = etree.SubElement(xml_group, 'group', {
                            'colspan': '6',
                            'col': '6',
                        })
                        etree.SubElement(xml_group, 'separator', {
                            'string': all_fields[field.name]['string'],
                            'colspan': '6',
                        })
                        etree.SubElement(xml_group, 'field', {
                            'name': "selection__" + field.name,
                            'colspan': '6',
                            'nolabel': '1',
                        })
                        etree.SubElement(xml_group, 'field', {
                            'name': field.name,
                            'colspan': '6',
                            'nolabel': '1',
                            'attrs': "{'invisible':[('selection__" +
                            field.name + "','=','remove')]}",
                        })
                    else:
                        all_fields["selection__" + field.name] = {
                            'type': 'selection',
                            'string': field_info[field.name]['string'],
                            'selection': [('set', 'Set'), ('remove', 'Remove')]
                        }
                        etree.SubElement(xml_group, 'field', {
                            'name': "selection__" + field.name,
                            'colspan': '2',
                        })
                        etree.SubElement(xml_group, 'field', {
                            'name': field.name,
                            'nolabel': '1',
                            'attrs': "{'invisible':[('selection__" +
                            field.name + "','=','remove')]}",
                            'colspan': '4',
                        })
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
            doc = etree.XML(result['arch'])
            for field in editing_data.field_ids:
                for node in doc.xpath("//field[@name='set_selection_" +
                                      field.name + "']"):
                    modifiers = json.loads(node.get("modifiers", '{}'))
                    modifiers.update({'invisible': [(
                        "selection__" + field.name, 'in', ('remove', 'set'))],
                        'required': [("selection__" + field.name, 'in',
                                      ('val_add', 'val_sub', 'val_mul',
                                       'val_div'))]}
                    )
                    node.set("modifiers", json.dumps(modifiers))
                for node in doc.xpath("//field[@name='" + field.name + "']"):
                    modifiers = json.loads(node.get("modifiers", '{}'))
                    attr_val = 'remove'
                    if field.ttype == "many2many":
                        attr_val = 'remove_m2m_all'
                    elif field.ttype == "one2many":
                        attr_val = 'remove_o2m'
                    modifiers.update({'invisible': [
                        ("selection__" + field.name, '=', attr_val)
                    ]})
                    node.set("modifiers", json.dumps(modifiers))
            result['arch'] = etree.tostring(doc)
        return result

    @api.model
    def create(self, vals):
        if (self._context.get('active_model') and
                self._context.get('active_ids')):
            model_obj = self.env[self._context.get('active_model')]
            model_rec = model_obj.browse(self._context.get('active_ids'))
            values = {}
            for key, val in vals.items():
                if key.startswith('selection_'):
                    split_key = key.split('__', 1)[1]
                    set_val = vals.get('set_selection_' + split_key)
                    if val == 'set':
                        values.update({split_key: vals.get(split_key, False)})
                    elif val == 'remove':
                        values.update({split_key: False})
                    elif val == 'remove_m2m':
                        if vals.get(split_key):
                            m2m_list = []
                            for m2m_id in vals.get(split_key)[0][2]:
                                m2m_list.append((3, m2m_id))
                            values.update({split_key: m2m_list})
                    elif val in ['remove_o2m', 'remove_m2m_all']:
                        values.update({split_key: [(5, 0, [])]})
                    elif val == 'add':
                        if vals.get(split_key, False):
                            m2m_list = []
                            for m2m_id in vals.get(split_key)[0][2]:
                                m2m_list.append((4, m2m_id))
                            values.update({split_key: m2m_list})

                    # Mathematical operations
                    elif val in ['val_add', 'val_sub', 'val_mul', 'val_div']:
                        split_val = vals.get(split_key, 0.0)
                        for data in model_rec:
                            split_key_data = data[split_key]
                            tot_val = 0
                            # Addition
                            if val == 'val_add':
                                if set_val == 'set_fix':
                                    tot_val = split_key_data + split_val
                                elif set_val == 'set_per':
                                    tot_val = split_key_data +\
                                        (split_key_data * split_val) / 100.0
                            # Subtraction
                            elif val == 'val_sub':
                                if set_val == 'set_fix':
                                    tot_val = split_key_data - split_val
                                elif set_val == 'set_per':
                                    tot_val = split_key_data -\
                                        (split_key_data * split_val) / 100.0
                            # Multiplication
                            elif val == 'val_mul':
                                if set_val == 'set_fix':
                                    tot_val = split_key_data * split_val
                                elif set_val == 'set_per':
                                    tot_val = split_key_data *\
                                        (split_key_data * split_val) / 100
                            # Division
                            elif val == 'val_div':
                                if set_val == 'set_fix':
                                    tot_val = split_key_data / split_val
                                elif set_val == 'set_per':
                                    tot_val = split_key_data /\
                                        (split_key_data * split_val) / 100
                            data.write({split_key: tot_val})
            if values:
                model_rec.write(values)
        return super(MassEditingWizard, self).create({})

    @api.multi
    def action_apply(self):
        return {'type': 'ir.actions.act_window_close'}
