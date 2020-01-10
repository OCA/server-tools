# © 2017 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from collections import OrderedDict
from odoo import api, models


def update_dict(data, fields):
    """Contruct a tree of fields.

    Example:

        {
            "name": True,
            "resource": True,
        }

    Order of keys is important.
    """
    field = fields[0]
    if len(fields) == 1:
        if field == '.id':
            field = 'id'
        data[field] = True
    else:
        if field not in data:
            data[field] = OrderedDict()
        update_dict(data[field], fields[1:])


def convert_dict(dict_parser):
    """Convert dict returned by update_dict to list consistent w/ Odoo API.

    The list is composed of strings (field names or aliases) or tuples.
    """
    parser = []
    for field, value in dict_parser.items():
        if value is True:
            parser.append(field)
        else:
            parser.append((field, convert_dict(value)))
    return parser


class IrExport(models.Model):
    _inherit = 'ir.exports'

    @api.multi
    def get_json_parser(self):
        """Creates a parser from ir.exports record and return it.

        The final parser can be used to "jsonify" records of ir.export's model.
        """
        self.ensure_one()
        dict_parser = OrderedDict()
        for line in self.export_fields:
            names = line.name.split('/')
            if line.alias:
                names = line.alias.split('/')
            update_dict(dict_parser, names)

        return convert_dict(dict_parser)
