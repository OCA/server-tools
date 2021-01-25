# Copyright 2017 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# Raphaël Reverdy <raphael.reverdy@akretion.com>
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _

from .utils import convert_simple_to_full_parser


class Base(models.AbstractModel):

    _inherit = "base"

    @api.model
    def __parse_field(self, parser_field):
        """Deduct how to handle a field from its parser."""
        return parser_field if isinstance(parser_field, tuple) else (parser_field, None)

    @api.model
    def _jsonify_bad_parser_error(self, field_name):
        raise UserError(_("Wrong parser configuration for field: `%s`") % field_name)

    def _function_value(self, record, function, field_name):
        if function in dir(record):
            method = getattr(self, function, None)
            return method(field_name)
        elif callable(function):
            return function(record, field_name)
        else:
            return self._jsonify_bad_parser_error(field_name)

    @api.model
    def _jsonify_value(self, field, value):
        """Override this function to support new field types."""
        if value is False and field.type != "boolean":
            value = None
        elif field.type == "date":
            value = fields.Date.to_date(value).isoformat()
        elif field.type == "datetime":
            # Ensures value is a datetime
            value = fields.Datetime.to_datetime(value)
            # Get the timestamp converted to the client's timezone.
            # This call also add the tzinfo into the datetime object
            value = fields.Datetime.context_timestamp(self, value)
            value = value.isoformat()
        return value

    @api.model
    def _add_json_key(self, values, json_key, value):
        """To manage defaults, you can use a specific resolver."""
        key_marshaller = json_key.split("=")
        key = key_marshaller[0]
        marshaller = key_marshaller[1] if len(key_marshaller) > 1 else None
        if marshaller == "list":  # sublist field
            if not values.get(key):
                values[key] = []
            values[key].append(value)
        else:
            values[key] = value

    @api.model
    def _jsonify_record(self, parser, rec, root):
        """Jsonify one record (rec). Private function called by jsonify."""
        for field in parser:
            field_dict, subparser = rec.__parse_field(field)
            field_name = field_dict["name"]
            json_key = field_dict.get("target", field_name)
            field = rec._fields[field_name]
            if field_dict.get("function"):
                function = field_dict["function"]
                value = self._function_value(rec, function, field_name)
            elif subparser:
                if not (field.relational or field.type == "reference"):
                    self._jsonify_bad_parser_error(field_name)
                value = [
                    self._jsonify_record(subparser, r, {}) for r in rec[field_name]
                ]
                if field.type in ("many2one", "reference"):
                    value = value[0] if value else None
            else:
                resolver = field_dict.get("resolver")
                value = rec._jsonify_value(field, rec[field.name])
                value = resolver.resolve(field, rec)[0] if resolver else value

            self._add_json_key(root, json_key, value)
        return root

    def jsonify(self, parser, one=False):
        """Convert the record according to the given parser.

        Example of (simple) parser:
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
        if isinstance(parser, list):
            parser = convert_simple_to_full_parser(parser)
        resolver = parser.get("resolver")

        results = [{} for record in self]
        parsers = {False: parser["fields"]} if "fields" in parser else parser["langs"]
        for lang in parsers:
            translate = lang or parser.get("language_agnostic")
            records = self.with_context(lang=lang) if translate else self
            for record, json in zip(records, results):
                self._jsonify_record(parsers[lang], record, json)

        results = resolver.resolve(results, self) if resolver else results
        return results[0] if one else results
