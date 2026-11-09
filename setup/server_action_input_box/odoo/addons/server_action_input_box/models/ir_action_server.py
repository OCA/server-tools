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
        protected_records = self._get_protected_ir_action_server_records()

        protected_record_names_in_self = [
            record.name for record in self if record in protected_records
        ]
        if any(record in protected_records for record in self):
            raise UserError(
                _("You are not allowed to modify this protected record:\n")
                + f"{protected_record_names_in_self}"
            )
        return super(IrActionServer, self).write(vals)

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
        return super(IrActionServer, self).unlink()
