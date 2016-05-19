# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


def update_dict(data, fields):
    field = fields[0]
    if len(fields) == 1:
        data[field] = True
    else:
        if field not in data:
            data[field] = {}
        update_dict(data[field], fields[1:])


def convert_dict(dict_parser):
    parser = []
    for field, value in dict_parser.iteritems():
        if value is True:
            parser.append(field)
        else:
            parser.append((field, convert_dict(value)))
    return parser


class IrExport(models.Model):
    _inherit = 'ir.exports'

    @api.multi
    def get_json_parser(self):
        self.ensure_one()
        dict_parser = {}
        for line in self.export_fields:
            update_dict(dict_parser, line.name.split('/'))
        return convert_dict(dict_parser)
