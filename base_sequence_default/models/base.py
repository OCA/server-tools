# Copyright 2023 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

import logging

from odoo import api, models

SEQUENCE_PREFIX = "base_sequence_default"
_logger = logging.getLogger(__name__)


class Base(models.AbstractModel):
    _inherit = "base"

    @api.model_create_multi
    def create(self, vals_list):
        """Produce sequenced defaults if DB is configured for that."""
        result = super().create(vals_list)
        # Get sequences for fields in this model
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
        for record in result:
            for seq in model_sequences:
                fname = seq.code[len(prefix) :]
                if fname not in record._fields:
                    _logger.warning(
                        "Ignoring sequence %s; missing field %s in model %s",
                        seq.code,
                        fname,
                        self._name,
                    )
                    continue
                if record[fname] in {False, "-"}:
                    record[fname] = seq.next_by_id()
        return result
