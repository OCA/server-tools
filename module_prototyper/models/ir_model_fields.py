# -*- coding: utf-8 -*-
# © 2010 - 2014 Savoir-faire Linux (<http://www.savoirfairelinux.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models
from openerp.tools.translate import _


class ir_model_fields(models.Model):
    """Addition of text fields to fields."""
    _inherit = "ir.model.fields"

    notes = fields.Text('Notes to developers.')
    helper = fields.Text('Helper')
    # TODO: Make column1 and 2 required if a model has a m2m to itself
    column1 = fields.Char(
        'Column1',
        help=_("name of the column referring to 'these' records in the "
               "relation table"),
    )
    column2 = fields.Char(
        'Column2',
        help=_("name of the column referring to 'those' records in the "
               "relation table"),
    )
    limit = fields.Integer('Read limit', help=_("Read limit"))
    client_context = fields.Char(
        'Context',
        help=_("Context to use on the client side when handling the field "
               "(python dictionary)"),
    )
