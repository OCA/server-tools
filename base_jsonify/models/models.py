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

    _inherit = "base"

    @api.model
    def __parse_field(self, parser_field):
        """Deduct how to handle a field from its parser."""
        return parser_field if isinstance(parser_field, tuple) else (parser_field, None)

    @api.model
    def convert_simple_to_full_parser(self, parser):
        def _f(f, function=None):
            field_split = f.split(":")
            field_dict = {"name": field_split[0]}
            if len(field_split) > 1:
                field_dict["alias"] = field_split[1]
            if function:
                field_dict["function"] = function
            return field_dict

        def _convert_parser(parser):
            result = []
            for line in parser:
                if isinstance(line, str):
                    result.append(_f(line))
                else:
                    f, sub = line
                    if callable(sub) or isinstance(sub, str):
                        result.append(_f(f, sub))
                    else:
                        result.append((_f(f), _convert_parser(sub)))
            return result

        return {"language_agnostic": False, "fields": _convert_parser(parser)}

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
    def _jsonify_value(self, record, field, resolver):
        # TODO: we should get default by field (eg: char field -> "")
        value = record[field.name]
        if value is False and field.type != "boolean":
            value = None
        elif field.type == "date":
            value = fields.Date.to_date(value).isoformat()
        elif field.type == "datetime":
            # Ensures value is a datetime
            value = fields.Datetime.to_datetime(value)
            # Get the timestamp converted to the client's timezone.
            # This call also add the tzinfo into the datetime object
            value = fields.Datetime.context_timestamp(record, value)
            value = value.isoformat()
        return self._resolve(resolver, field, record)[0] if resolver else value

    @api.model
    def _resolve(self, resolver, *args):
        if isinstance(resolver, int):
            resolver = self.env["ir.exports.resolver"].browse(resolver)
        return resolver.eval(*args)

    @api.model
    def _jsonify_record(self, parser, rec, root):
        for field in parser:
            field_dict, subparser = rec.__parse_field(field)
            field_name = field_dict["name"]
            json_key = field_dict.get("alias", field_name)
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
                value = self._jsonify_value(rec, field, field_dict.get("resolver"))
            if json_key.endswith("*"):  # sublist field
                key = json_key[:-1]
                if not root.get(key):
                    root[key] = []
                root[key].append(value)
            else:
                root[json_key] = value
        return root

    @api.multi
    def jsonify(self, parser):
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
        return a list of object even if there is only one element in input

        By default the key into the json is the name of the field extracted
        from the model. If you need to specify an alternate name to use as
        key, you can define your mapping as follow into the parser definition:

        parser = [
             'field_name:json_key'
        ]

        """
        if isinstance(parser, list):
            parser = self.convert_simple_to_full_parser(parser)
        resolver = parser.get("resolver")

        results = [{} for record in self]
        parsers = {False: parser["fields"]} if "fields" in parser else parser["langs"]
        for lang in parsers:
            translate = lang or parser.get("language_agnostic")
            records = self.with_context(lang=lang) if translate else self
            for record, json in zip(records, results):
                self._jsonify_record(parsers[lang], record, json)

        return self._resolve(resolver, results, self) if resolver else results
