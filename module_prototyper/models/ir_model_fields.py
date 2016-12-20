# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2010 - 2014 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import fields, models


class IrModelFields(models.Model):
    """Addition of text fields to fields."""
    _inherit = "ir.model.fields"

    notes = fields.Text('Notes to developers.')
    helper = fields.Text('Helper')
    # TODO: Make column1 and 2 required if a model has a m2m to itself
    column1 = fields.Char(
        'Column1',
        help="name of the column referring to 'these' records in the "
             "relation table",
    )
    column2 = fields.Char(
        'Column2',
        help="name of the column referring to 'those' records in the "
             "relation table",
    )
    limit = fields.Integer('Read limit', help="Read limit")
    client_context = fields.Char(
        'Context',
        help="Context to use on the client side when handling the field "
             "(python dictionary)",
    )
