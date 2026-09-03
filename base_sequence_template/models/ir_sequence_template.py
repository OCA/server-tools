# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class IrSequenceTemplate(models.Model):
    _name = "ir.sequence.template"
    _description = "Sequence Template"
    _order = "name"
    _allow_sudo_commands = False

    active = fields.Boolean(default=True)

    name = fields.Char(required=True)
    code = fields.Char(string="Sequence Code")
    implementation = fields.Selection(
        [("standard", "Standard"), ("no_gap", "No gap")],
        required=True,
        default="standard",
    )
    prefix = fields.Char(help="Prefix value of the record for the sequence", trim=False)
    suffix = fields.Char(help="Suffix value of the record for the sequence", trim=False)
    number_increment = fields.Integer(string="Step", required=True, default=1)
    padding = fields.Integer(string="Sequence Size", required=True, default=0)

    sequence_ids = fields.One2many("ir.sequence", "template_id")
    sequence_count = fields.Integer(compute="_compute_sequence_count")

    @api.depends("sequence_ids")
    def _compute_sequence_count(self):
        for record in self:
            record.sequence_count = len(record.sequence_ids)

    def action_view_sequences(self):
        self.ensure_one()
        return {
            "name": "Sequences",
            "type": "ir.actions.act_window",
            "res_model": "ir.sequence",
            "view_mode": "list,form",
            "domain": [("template_id", "=", self.id)],
            "context": {"default_template_id": self.id},
        }

    def action_generate_sequences(self):
        return self.open_generate_sequences_wizard()

    def open_generate_sequences_wizard(self):
        return {
            "name": "Generate Sequences",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "generate.company.sequences.wizard",
            "target": "new",
            "view_id": self.env.ref(
                "base_sequence_template.view_generate_company_sequences_wizard_form"
            ).id,
            "context": {
                "default_template_ids": self.ids,
            },
        }
