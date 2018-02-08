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

from odoo import models, fields, api
from lxml import etree


class AttributeOptionWizard(models.TransientModel):
    _name = "attribute.option.wizard"
    _rec_name = 'attribute_id'

    attribute_id = fields.Many2one(
        'attribute.attribute',
        'Product Attribute',
        required=True,
        default=lambda self: self.env.context.get('attribute_id', False),
    )

    @api.multi
    def validate(self):
        return True

    @api.model
    def create(self, vals):
        attr_obj = self.env["attribute.attribute"]
        attr = attr_obj.browse(vals['attribute_id'])

        opt_obj = self.env["attribute.option"]

        for op_id in (
            vals.get("option_ids") and vals['option_ids'][0][2] or []
        ):
            model = attr.relation_model_id.model

            name = self.env[model].browse(op_id).name_get()[0][1]
            opt_obj.create({
                'attribute_id': vals['attribute_id'],
                'name': name,
                'value_ref': "%s,%s" % (attr.relation_model_id.model, op_id)
            })

        res = super(AttributeOptionWizard, self).create(vals)

        return res

    @api.model
    def fields_view_get(
        self, view_id=None, view_type='form',
        toolbar=False, submenu=False
    ):
        context = self.env.context
        res = super(AttributeOptionWizard, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)

        if view_type == 'form' and context and context.get("attribute_id"):
            attr_obj = self.env["attribute.attribute"]
            attr = attr_obj.browse(context.get("attribute_id"))
            model = attr.relation_model_id

            relation = model.model

            res['fields'].update({
                'option_ids': {
                    'domain': [('id', 'not in', attr.option_ids.ids)],
                    'string': "Options",
                    'type': 'many2many',
                    'relation': relation,
                    'required': True,
                }
            })

            eview = etree.fromstring(res['arch'])
            options = etree.Element('field', name='option_ids', colspan='6')
            placeholder = eview.xpath(
                "//separator[@string='options_placeholder']")[0]
            placeholder.getparent().replace(placeholder, options)
            res['arch'] = etree.tostring(eview, pretty_print=True)

        return res
