# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# Raphaël Reverdy <raphael.reverdy@akretion.com>
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _


class Base(models.AbstractModel):

    _inherit = 'base'

    @api.model
    def __parse_field(self, parser_field):
        """
        Deducts how to handle a field from its parser
        """
        field_name = parser_field
        subparser = None
        if isinstance(parser_field, tuple):
            field_name, subparser = parser_field
        json_key = field_name
        if ':' in field_name:
            field_name, json_key = field_name.split(':')
        return field_name, json_key, subparser

    def jsonify(self, parser, one=False):
        """Convert the record according to the given parser.

        Example of parser:
            parser = [
                'name',
                'number',
                'create_date',
                ('partner_id', ['id', 'display_name', 'ref'])
                ('shipping_id', callable)
                ('delivery_id', "record_method")
                ('line_id', ['id', ('product_id', ['name']), 'price_unit'])
            ]

        In order to be consistent with the odoo api the jsonify method always
        return a list of object even if there is only one element in input.
        You can change this behavior by passing `one=True` to get only one element.

        By default the key into the json is the name of the field extracted
        from the model. If you need to specify an alternate name to use as
        key, you can define your mapping as follow into the parser definition:

        parser = [
             'field_name:json_key'
        ]

        """
        if one:
            self.ensure_one()

        result = []

        for rec in self:
            res = {}
            for field in parser:
                field_name, json_key, subparser = self.__parse_field(field)
                if subparser:
                    res[json_key] = rec._jsonify_value_subparser(field_name, subparser)
                else:
                    res[json_key] = rec._jsonify_value(field_name)
            result.append(res)
        if one:
            return result[0] if result else {}
        return result

    def _jsonify_value(self, field_name):
        field = self._fields[field_name]
        value = self[field_name]
        # TODO: we should get default by field (eg: char field -> "")
        if value is False and field.type != "boolean":
            value = None
        elif field.type == "date":
            value = fields.Date.from_string(value).isoformat()
        elif field.type == "datetime":
            # Ensures value is a datetime
            value = fields.Datetime.from_string(value)
            # Get the timestamp converted to the client's timezone.
            # This call also add the tzinfo into the datetime object
            value = fields.Datetime.context_timestamp(self, value)
            value = value.isoformat()
        elif field.type in ("many2one", "reference"):
            value = value.display_name if value else None
        elif field.type in ("one2many", "many2many"):
            value = [v.display_name for v in value]
        return value

    def _jsonify_value_subparser(self, field_name, subparser):
        value = None
        if callable(subparser):
            # a simple function
            value = subparser(self, field_name)
        elif isinstance(subparser, str):
            # a method on the record itself
            method = getattr(self, subparser, None)
            if method:
                value = method(field_name)
            else:
                self._jsonify_bad_parser_error(field_name)
        else:
            field = self._fields[field_name]
            if not (field.relational or field.type == "reference"):
                self._jsonify_bad_parser_error(field_name)
            rec_value = self[field_name]
            value = rec_value.jsonify(subparser) if rec_value else []
            if field.type in ("many2one", "reference"):
                value = value[0] if value else None
        return value

    def _jsonify_bad_parser_error(self, field_name):
        raise UserError(_("Wrong parser configuration for field: `%s`") % field_name)
