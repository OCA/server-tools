# -*- coding: utf-8 -*-
# © 2017 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# Raphaël Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.exceptions import UserError
from odoo.tools.translate import _


class Base(models.AbstractModel):

    _inherit = 'base'

    @api.model
    def __parse_field(self, parser_field):
        field_name = parser_field
        subparser = None
        if isinstance(parser_field, tuple):
            field_name, subparser = parser_field
        json_key = field_name
        if ':' in field_name:
            field_name, json_key = field_name.split(':')
        return field_name, json_key, subparser


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

        By default the key into the json is the name of the field extracted
        from the model. If you need to specify an alternate name to use as key, you
        can define your mapping as follow into the parser definition:

        parser = [
             'field_name:json_key'
        ]

        """
        result = []
        empty_value = {
            'char': None,
            'int': None,
            # 'float': None, TODO:  0.0 != False
            'text': None,
            }

        for rec in self:
            res = {}
            for field in parser:
                field_name, json_key, subparser = self.__parse_field(field)
                field_type = rec._fields[field_name].type
                if subparser:
                    if field_type in ('one2many', 'many2many'):
                        res[json_key] = rec[field_name].jsonify(subparser)
                    elif field_type in ('many2one', 'reference'):
                        if rec[field_name]:
                            res[json_key] = rec[field_name].jsonify(subparser)[0]
                        else:
                            res[json_key] = None
                    else:
                        raise UserError(_('Wrong parser configuration'))
                else:
                    res[json_key] = rec[field_name]
                    if not res[json_key] and field_type in empty_value:
                        res[json_key] = empty_value[field_type]
            result.append(res)
        return result
