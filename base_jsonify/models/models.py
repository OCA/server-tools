# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models
from openerp.exceptions import Warning as UserError
from openerp.tools.translate import _


@api.multi
def jsonify(self, parser):
    """ Convert the record according to the parser given
    Example of parser:
        parser = [
            'name',
            'number',
            'create_date',
            ('partner_id', ['id', 'display_name', 'ref'])
            ('line_id', ['id', ('product_id', ['name']), 'price_unit'])
        ]

    In order to be consitent with the odoo api the jsonify method always
    return a list of object even if there is only one element in input
    """
    result = []
    for rec in self:
        res = {}
        for field in parser:
            if isinstance(field, tuple):
                field_name, subparser = field
                field_type = rec._fields[field_name].type
                if field_type in ('one2many', 'many2many'):
                    res[field_name] = rec[field_name].jsonify(subparser)
                elif field_type == 'many2one':
                    data = rec[field_name].jsonify(subparser)
                    if data:
                        res[field_name] = data[0]
                    else:
                        res[field_name] = None
                else:
                    raise UserError(_('Wrong parser configuration'))
            else:
                res[field] = rec[field]
        result.append(res)
    return result


models.Model.jsonify = jsonify
