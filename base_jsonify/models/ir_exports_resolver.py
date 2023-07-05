# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.tools.safe_eval import safe_eval

help_message = [
    "Compute the result from 'value' by setting the variable 'result'.",
    "For fields resolvers:",
    ":param name: name of the field",
    ":param value: value of the field",
    ":param field_type: type of the field",
    "For global resolvers:",
    ":param value: json dict",
    ":param record: the record",
]


class FieldResolver(models.Model):
    """Arbitrary function to process a field or a dict at export time.
    """

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
                    "value": record[param.name],
                    "name": param.name,
                    "field_type": param.type,
                    "context": context,
                }
                safe_eval(self.python_code, values, mode="exec", nocopy=True)
                result.append(values["result"])
        return result
