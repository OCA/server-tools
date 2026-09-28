# Copyright 2024 jesanmor - Jesús Sánchez <jesanmor.dev@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ServerActionInputBoxLine(models.Model):
    _name = "server.action.input.box.line"
    _description = "Server Action Input Box Line"

    server_action_input_box_id = fields.Many2one(
        "server.action.input.box",
        string="Server action input box",
        readonly=True,
        ondelete="cascade",
    )
    name = fields.Char("Unique Name", required=True)
    parameter_label = fields.Char(required=True)
    data_type = fields.Selection(
        [
            ("string", "Text"),
            ("int", "Integer"),
            ("float", "Floating Point"),
            ("bool", "Boolean"),
        ],
        default="string",
        required=True,
    )

    def write(self, vals):
        if "name" in vals:
            if not vals["name"].isidentifier():
                raise UserError(
                    _(
                        "'%s' is not a valid parameter name. \
                    Remove spaces and special characters or numbers at the beginning.",
                        vals["name"],
                    )
                )
        record = super(ServerActionInputBoxLine, self).write(vals)
        return record

    @api.model_create_multi
    def create(self, vals):
        record = super(ServerActionInputBoxLine, self).create(vals)
        for rec in record:
            if not rec.name.isidentifier():
                raise UserError(
                    _(
                        "'%s' is not a valid parameter name. \
                        Remove spaces and special characters or numbers at the beginning.",
                        rec.name,
                    )
                )
        return record
