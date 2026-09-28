# Copyright 2024 jesanmor - Jesús Sánchez <jesanmor.dev@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import _, models
from odoo.exceptions import UserError


class IrActionServer(models.Model):
    _inherit = "ir.actions.server"

    def _get_protected_ir_action_server_records(self):
        protected_records = (
            self.env["server.action.input.box"].search([]).mapped("ir_action_server_id")
        )
        return protected_records

    def write(self, vals):
        server_action_input_box = self.env["server.action.input.box"].search(
            [("ir_action_server_id", "=", self.id)]
        )
        if server_action_input_box:
            code = server_action_input_box._code_ir_action_server()
            if server_action_input_box.active_action:
                model_id = server_action_input_box.model_id.id
            else:
                model_id = None
            vals = {
                "name": server_action_input_box.name,
                "model_id": server_action_input_box.model_id.id,
                "state": "code",
                "code": code,
                "binding_model_id": model_id,
                "binding_type": "action",
            }
        return super().write(vals)

    def unlink(self):
        protected_records = self._get_protected_ir_action_server_records()
        protected_record_names_in_self = [
            record.name for record in self if record in protected_records
        ]
        if any(record in protected_records for record in self):
            raise UserError(
                _("You are not allowed to delete these protected records:\n")
                + f"{protected_record_names_in_self}"
            )
        return super().unlink()
