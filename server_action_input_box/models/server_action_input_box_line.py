# Copyright 2024 jesanmor - Jesús Sánchez <jesanmor.dev@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


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

    @api.constrains("name", "server_action_input_box_id")
    def _check_name(self):
        for line in self:
            if not line.name.isidentifier():
                raise ValidationError(
                    _(
                        "'%s' is not a valid parameter name. \
                    Remove spaces and special characters or numbers at the beginning.",
                        line.name,
                    )
                )
            domain = [
                ("server_action_input_box_id", "=", line.server_action_input_box_id.id),
                ("name", "=", line.name),
                ("id", "!=", line.id),
            ]
            if self.search_count(domain):
                raise ValidationError(
                    _("the unique name '%s' cannot be duplicated", line.name)
                )
