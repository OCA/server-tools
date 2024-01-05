# © 2017 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from collections import OrderedDict

from odoo import fields, models
from odoo.tools import ormcache


def partition(line, accessor):
    """Partition a recordset according to an accessor (e.g. a lambda).
    Returns a dictionary whose keys are the values obtained from accessor,
    and values are the items that have this value.
    Example: partition([{"name": "ax"}, {"name": "by"}], lambda x: "x" in x["name"])
             => {True: [{"name": "ax"}], False: [{"name": "by"}]}
    """
    result = {}
    for item in line:
        key = accessor(item)
        if key not in result:
            result[key] = []
        result[key].append(item)
    return result


def update_dict(data, fields, options):
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
        if field == ".id":
            field = "id"
        data[field] = (True, options)
    else:
        if field not in data:
            data[field] = (False, OrderedDict())
        update_dict(data[field][1], fields[1:], options)


def convert_dict(dict_parser):
    """Convert dict returned by update_dict to list consistent w/ Odoo API.

    The list is composed of strings (field names or targets) or tuples.
    """
    parser = []
    for field, value in dict_parser.items():
        if value[0] is True:  # is a leaf
            parser.append(field_dict(field, value[1]))
        else:
            parser.append((field_dict(field), convert_dict(value[1])))
    return parser


def field_dict(field, options=None):
    """Create a parser dict for the field field."""
    result = {"name": field.split(":")[0]}
    if len(field.split(":")) > 1:
        result["target"] = field.split(":")[1]
    for option in options or {}:
        if options[option]:
            result[option] = options[option]
    return result


class IrExports(models.Model):
    _inherit = "ir.exports"

    language_agnostic = fields.Boolean(
        default=False,
        help="If set, will set the lang to False when exporting lines without lang,"
        " otherwise it uses the lang in the given context to export these fields",
    )

    global_resolver_id = fields.Many2one(
        comodel_name="ir.exports.resolver",
        string="Custom global resolver",
        domain="[('type', '=', 'global')]",
        help="If set, will apply the global resolver to the result",
    )

    @ormcache(
        "self.language_agnostic",
        "self.global_resolver_id.id",
        "tuple(self.export_fields.mapped('write_date'))",
    )
    def get_json_parser(self):
        """Creates a parser from ir.exports record and return it.

        The final parser can be used to "jsonify" records of ir.export's model.
        """
        self.ensure_one()
        parser = {}
        lang_to_lines = partition(self.export_fields, lambda _l: _l.lang_id.code)
        lang_parsers = {}
        for lang in lang_to_lines:
            dict_parser = OrderedDict()
            for line in lang_to_lines[lang]:
                names = line.name.split("/")
                if line.target:
                    names = line.target.split("/")
                function = line.instance_method_name
                options = {"resolver": line.resolver_id, "function": function}
                update_dict(dict_parser, names, options)
            lang_parsers[lang] = convert_dict(dict_parser)
        if list(lang_parsers.keys()) == [False]:
            parser["fields"] = lang_parsers[False]
        else:
            parser["langs"] = lang_parsers
        if self.global_resolver_id:
            parser["resolver"] = self.global_resolver_id
        if self.language_agnostic:
            parser["language_agnostic"] = self.language_agnostic
        return parser
