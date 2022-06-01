# Copyright 2020 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models
from odoo.tools.safe_eval import safe_eval

help_message = [
    "Compute the result from 'value' by setting the variable 'result'.",
    "\n" "For fields resolvers:",
    ":param record: the record",
    ":param name: name of the field",
    ":param value: value of the field",
    ":param field_type: type of the field",
    "\n" "For global resolvers:",
    ":param value: JSON dict",
    ":param record: the record",
    "\n"
    "In both types, you can override the final json key."
    "\nTo achieve this, simply return a dict like: "
    "\n{'result': {'_value': $value, '_json_key': $new_json_key}}",
]


class FieldResolver(models.Model):
    """Arbitrary function to process a field or a dict at export time."""

    _name = "ir.exports.resolver"
    _description = "Export Resolver"

    name = fields.Char()
    type = fields.Selection([("field", "Field"), ("global", "Global")])
    python_code = fields.Text(
        string="Python Code",
        default="\n".join(["# " + h for h in help_message] + ["result = value"]),
        help="\n".join(help_message),
    )

    def resolve(self, param, records):
        self.ensure_one()
        result = []
        context = records.env.context
        if self.type == "global":
            assert len(param) == len(records)
            for value, record in zip(param, records):
                values = {"value": value, "record": record, "context": context}
                safe_eval(self.python_code, values, mode="exec", nocopy=True)
                result.append(values["result"])
        else:  # param is a field
            for record in records:
                values = {
                    "record": record,
                    "value": record[param.name],
                    "name": param.name,
                    "field_type": param.type,
                    "context": context,
                }
                safe_eval(self.python_code, values, mode="exec", nocopy=True)
                result.append(values["result"])
        return result
