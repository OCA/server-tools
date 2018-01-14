# -*- coding: utf-8 -*-
# Florent de Labarre - 2018

import itertools
import xml.etree.ElementTree as ElementTree
import xml.dom.minidom as minidom
import base64

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class BaseExportXml(models.TransientModel):
    _name = 'base.export.xml'
    _description = 'Base Export XML'

    model_ids = fields.Many2many('ir.model', string='Model', required=True, domain=[('transient', '=', False)])
    with_binary = fields.Boolean('With Binary', default=False)
    with_no_update = fields.Boolean('With NoUpdate', default=False)
    with_archived = fields.Boolean('With Archived', default=False)
    default_export = fields.Char('Default Export', required=True, default='__export__')
    file_data = fields.Binary()
    filename = fields.Char()

    @api.multi
    def action_export(self):
        self.ensure_one()

        root = ElementTree.Element("odoo")
        if self.with_no_update:
            data = ElementTree.SubElement(root, "data", noupdate="1")
        else:
            data = root
        for model in self.model_ids.filtered(lambda x: not x.transient):

            Model = self.env[model.model]
            if Model._abstract:
                continue

            records = Model.with_context(active_test=not self.with_archived).search([])

            model_fields = self.get_fields(Model)

            for record in records:
                # print(record)
                xml_id = self._export_xml_id(record)
                doc = ElementTree.SubElement(data, "record", id=xml_id, model=model.model)

                for field in model_fields:
                    # print(field, record[field.get('name')])
                    field_name = field.get('name')
                    field_type = field.get('type')
                    if not record[field_name]:
                        continue

                    if field_type == 'id':
                        continue

                    if field_type == 'binary' and not self.with_binary:
                        continue

                    value = record[field_name]

                    if field_type == 'many2one':
                        xml_id = self._export_xml_id(value)
                        ElementTree.SubElement(doc, "field", name=field_name, ref=xml_id)

                    elif field_type == 'many2many':
                        xml_ids = ''
                        for v in value:
                            xml_ids += "ref('%s'), " % self._export_xml_id(v)
                        xml_ids = '[(6, 0, [ %s])]' % xml_ids
                        ElementTree.SubElement(doc, "field", name=field_name, eval=xml_ids)

                    elif field_type == 'boolean':
                        ElementTree.SubElement(doc, "field", name=field_name, eval='%s' % value)

                    elif field_type == 'selection':
                        ElementTree.SubElement(doc, "field", name=field_name).text = value

                    else:
                        field = record._fields[field_name]
                        converted_value = field.convert_to_export(value, record)
                        ElementTree.SubElement(doc, "field", name=field_name).text = converted_value

        xmlstr = ElementTree.tostring(root)

        xml = minidom.parseString(xmlstr)
        pretty_xml_as_string = xml.toprettyxml()

        self.write({'file_data': base64.b64encode(pretty_xml_as_string.encode('utf-8')),
                    'filename': _('data_%s.xml') % (fields.Datetime.now())})
        action = {
            'name': 'File',
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=base.export.xml&id=%s&filename_field=filename&field=file_data&download=true&filename=%s" % (self.id, self.filename),
            'target': 'new',
        }
        return action

    def _export_xml_id(self, value):
        """ Return a valid xml_id for the record ``value``. """
        if not value._is_an_ordinary_table():
            raise Exception(
                "You can not export the column ID of model %s, because the "
                "table %s is not an ordinary table."
                % (value._name, value._table))
        ir_model_data = value.sudo().env['ir.model.data']
        data = ir_model_data.search([('model', '=', value._name), ('res_id', '=', value.id)])
        if data:
            if data[0].module:
                return '%s.%s' % (data[0].module, data[0].name)
            else:
                return data[0].name
        else:
            postfix = 0
            name = '%s_%s' % (value._table, value.id)
            while ir_model_data.search([('module', '=', '__export__'), ('name', '=', name)]):
                postfix += 1
                name = '%s_%s_%s' % (value._table, value.id, postfix)
            ir_model_data.create({
                'model': value._name,
                'res_id': value.id,
                'module': self.default_export,
                'name': name,
            })
            return '%s.%s' % (self.default_export, name)

    def get_fields(self, Model):
        importable_fields = [{
            'name': 'id',
            'string': _("External ID"),
            'required': False,
            'type': 'id',
        }]
        model_fields = Model.fields_get()
        blacklist = models.MAGIC_COLUMNS + [Model.CONCURRENCY_CHECK_FIELD]
        for name, field in model_fields.items():
            if name in blacklist:
                continue
            if field.get('deprecated', False) is not False:
                continue
            if field.get('type') in ('one2many'):
                continue
            if field.get('readonly'):
                continue
            field_value = {
                'name': name,
                'string': field['string'],
                'required': bool(field.get('required')),
                'type': field['type'],
            }

            importable_fields.append(field_value)

        return importable_fields
