# Copyright 2023 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo import api, models

SEQUENCE_PREFIX = "base_sequence_default"


class Base(models.AbstractModel):
    _inherit = "base"

    @api.model
    def default_get(self, fields_list):
        """Produce sequenced defaults if DB is configured for that."""
        res = super().default_get(fields_list)
        prefix = f"{SEQUENCE_PREFIX}.{self._name}.fields."
        model_sequences = (
            self.env["ir.sequence"]
            .sudo()
            .search(
                [
                    ("code", "=like", f"{prefix}%"),
                    ("company_id", "in", [self.env.company.id, False]),
                ],
                order="company_id",
            )
        )
        sequences_by_field = {seq.code[len(prefix) :]: seq for seq in model_sequences}
        for fname in fields_list:
            try:
                seq = sequences_by_field[fname]
            except KeyError:
                # No sequence? No problem
                continue
            res[fname] = seq.next_by_id()
        return res
