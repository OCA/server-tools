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

from openerp import models, fields, api, _


class AttributeOption(models.Model):
    _name = "attribute.option"
    _description = "Attribute Option"
    _order = "sequence"

    @api.model
    def _get_model_list(self):
        models = self.env['ir.model'].search([])
        return [(m.model, m.name) for m in models]

    name = fields.Char(
        'Name',
        translate=True,
        required=True,
    )

    value_ref = fields.Reference(
        _get_model_list,
        'Reference',
    )

    attribute_id = fields.Many2one(
        'attribute.attribute',
        'Product Attribute',
        required=True,
    )

    sequence = fields.Integer('Sequence')

    def name_change(self, cr, uid, ids, name, relation_model_id, context=None):
        if relation_model_id:
            warning = {
                'title': _('Error!'),
                'message': _(
                    "Use the 'Load Options' button "
                    "instead to select appropriate "
                    "model references'"),
            }
            return {"value": {"name": False}, "warning": warning}
        else:
            return True
