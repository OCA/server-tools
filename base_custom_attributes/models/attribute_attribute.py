# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
#   base_attribute.attributes for OpenERP                                     #
#   Copyright (C) 2011 Akretion Benoît GUILLOT <benoit.guillot@akretion.com>  #
#   Copyright (C) 2013 Akretion Raphaël VALYI <raphael.valyi@akretion.com>    #
#   Copyright (C) 2015 Savoir-faire Linux                                     #
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

from odoo import models, fields, _, exceptions, api
from odoo.osv.orm import setup_modifiers
from lxml import etree
import ast
import re

try:
    from unidecode import unidecode
except ImportError as err:
    _logger.debug(err)


def safe_column_name(string):
    """ Prevent portability problem in database column name
    with other DBMS system
    Use case : if you synchronise attributes with other applications """
    string = unidecode(string.replace(' ', '_').lower())
    return re.sub(r'[^0-9a-z_]', '', string)


class AttributeAttribute(models.Model):
    _name = "attribute.attribute"
    _description = "Attribute"
    _inherits = {'ir.model.fields': 'field_id'}

    @api.model
    def _build_attribute_field(self, page, attribute):
        parent = etree.SubElement(page, 'group', colspan="2", col="4")
        kwargs = {'name': "%s" % attribute.name}

        if attribute.ttype in ['many2many', 'text']:
            parent = etree.SubElement(parent, 'group', colspan="2", col="4")
            etree.SubElement(
                parent,
                'separator',
                string="%s" % attribute.field_description,
                colspan="4")
            kwargs['nolabel'] = "1"

        if attribute.ttype in ['many2one', 'many2many']:
            if attribute.relation_model_id:
                # attribute.domain is a string, it may be an empty list
                try:
                    domain = ast.literal_eval(attribute.domain)
                except ValueError:
                    domain = None
                if domain:
                    kwargs['domain'] = attribute.domain
                else:
                    ids = [op.value_ref.id for op in attribute.option_ids]
                    kwargs['domain'] = "[('id', 'in', %s)]" % ids
            else:
                kwargs['domain'] = "[('attribute_id', '=', %s)]" % (
                    attribute.attribute_id.id)

        kwargs['context'] = "{'default_attribute_id': %s}" % (
            attribute.attribute_id.id)

        kwargs['required'] = str(
            attribute.required or attribute.required_on_views)

        field = etree.SubElement(parent, 'field', **kwargs)
        setup_modifiers(field, self.fields_get(attribute.name))

        return parent

    @api.model
    def _build_attributes_notebook(self, attribute_group_ids):
        notebook = etree.Element('notebook', name="attributes_notebook",
                                 colspan="4")
        toupdate_fields = []
        grp_obj = self.env['attribute.group']
        for group in grp_obj.browse(attribute_group_ids):
            page = etree.SubElement(notebook, 'page',
                                    string=group.name.capitalize())
            for attribute in group.attribute_ids:
                if attribute.name not in toupdate_fields:
                    toupdate_fields.append(attribute.name)
                    self._build_attribute_field(page, attribute)
        return notebook, toupdate_fields

    @api.onchange('relation_model_id')
    def relation_model_id_change(self):
        "removed selected options as they would be inconsistent"
        self.option_ids = [(5, 0)]

    @api.multi
    def button_add_options(self):
        self.ensure_one()
        return {
            'context': "{'attribute_id': %s}" % (self.id),
            'name': _('Options Wizard'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'attribute.option.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    field_id = fields.Many2one(
        'ir.model.fields',
        'Ir Model Fields',
        required=True,
        ondelete="cascade"
    )

    attribute_type = fields.Selection([
        ('char', 'Char'),
        ('text', 'Text'),
        ('select', 'Select'),
        ('multiselect', 'Multiselect'),
        ('boolean', 'Boolean'),
        ('integer', 'Integer'),
        ('date', 'Date'),
        ('datetime', 'Datetime'),
        ('binary', 'Binary'),
        ('float', 'Float')],
        'Type', required=True,
    )

    serialized = fields.Boolean(
        'Field serialized',
        help="If serialized, the field will be stocked in the serialized "
        "field: attribute_custom_tmpl or attribute_custom_variant "
        "depending on the field based_on"
    )

    option_ids = fields.One2many(
        'attribute.option',
        'attribute_id',
        'Attribute Options',
    )

    create_date = fields.Datetime('Created date', readonly=True)

    relation_model_id = fields.Many2one(
        'ir.model', 'Relational Model',
    )

    required_on_views = fields.Boolean(
        'Required (on views)',
        help="If activated, the attribute will be mandatory on the views, "
        "but not in the database",
    )

    @api.model
    def create(self, vals):
        """ Create an attribute.attribute

        When a `field_id` is given, the attribute will be linked to the
        existing field. The use case is to create an attribute on a field
        created with Python `fields`.

        """
        if vals.get('field_id'):
            # When a 'field_id' is given, we create an attribute on an
            # existing 'ir.model.fields'.  As this model `_inherits`
            # 'ir.model.fields', calling `create()` with a `field_id`
            # will call `write` in `ir.model.fields`.
            # When the existing field is not a 'manual' field, we are
            # not allowed to write on it. So we call `create()` without
            # changing the fields values.
            field_obj = self.env['ir.model.fields']
            field = field_obj.browse(vals['field_id'])

            if vals.get('serialized'):
                raise exceptions.ValidationError(
                    _('Error'),
                    _("Can't create a serialized attribute on "
                      "an existing ir.model.fields (%s)") % field.name)

            if field.state != 'manual':
                # The ir.model.fields already exists and we want to map
                # an attribute on it. We can't change the field so we
                # won't add the ttype, relation and so on.
                return super(AttributeAttribute, self).create(vals)

        if vals.get('relation_model_id'):
            model = self.env['ir.model'].browse(vals['relation_model_id'])
            relation = model.model
        else:
            relation = 'attribute.option'

        attr_type = vals.get('attribute_type')

        if attr_type == 'select':
            vals['ttype'] = 'many2one'
            vals['relation'] = relation

        elif attr_type == 'multiselect':
            vals['ttype'] = 'many2many'
            vals['relation'] = relation
            vals['serialized'] = True

        else:
            vals['ttype'] = attr_type

        if vals.get('serialized'):
            field_obj = self.env['ir.model.fields']

            serialized_fields = field_obj.search([
                ('ttype', '=', 'serialized'),
                ('model_id', '=', vals['model_id']),
                ('name', '=', 'x_custom_json_attrs'),
            ])

            if serialized_fields:
                vals['serialization_field_id'] = serialized_fields[0].id

            else:
                f_vals = {
                    'name': u'x_custom_json_attrs',
                    'field_description': u'Serialized JSON Attributes',
                    'ttype': 'serialized',
                    'model_id': vals['model_id'],
                }

                vals['serialization_field_id'] = field_obj.with_context(
                    {'manual': True}).create(f_vals).id

        vals['state'] = 'manual'
        return super(AttributeAttribute, self).create(vals)

    @api.onchange('field_description')
    def onchange_field_description(self):
        if self.field_description and not self.create_date:
            self.name = unicode(
                'x_' + safe_column_name(self.field_description))

    @api.onchange('name')
    def onchange_name(self):
        name = self.name

        if not name.startswith('x_'):
            self.name = u'x_%s' % name
