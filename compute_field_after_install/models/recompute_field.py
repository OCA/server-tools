# Copyright 2025 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import logging

from odoo import api, fields, models
from odoo.exceptions import Warning as UserError
from odoo.tools.translate import _

from odoo.tools import config

_logger = logging.getLogger(__name__)


class RecomputeField(models.Model):
    _name = "recompute.field"
    _description = "Recompute Field"

    model = fields.Char(required=True)
    field = fields.Char(required=True)
    last_id = fields.Integer(
        help="Last record ID on which computing have been executed"
    )

    step = fields.Integer(
        required=True,
        help="Recomputing batch size.",
        compute="_compute_default_step",
        store=True,
        readonly=False,
        precompute=True,
    )
    state = fields.Selection(
        [
            ("todo", "Todo"),
            ("done", "Done"),
        ]
    )

    @api.depends("model", "field")
    def _compute_default_step(self):
        for recompute_field in self:
            model = recompute_field.model.replace(".", "_")
            recompute_field.step = config.get(
                f"computed_fields_batch_size__{model}__{recompute_field.field}",
                config.get(
                    f"computed_fields_batch_size__{model}",
                    config.get("computed_fields_batch_size", 1000),
                ),
            )

    @api.constrains("step")
    def _check_step(self):
        for recompute_field in self:
            if recompute_field.step <= 0:
                raise UserError(_("Step must be greater than 0"))

    @api.model
    def _run_all(self):
        return self.search([("state", "=", "todo")]).run()

    def run(self):
        for task in self:
            cursor = self.env.cr
            model = self.env[task.model]

            while True:
                _logger.info(
                    "Recompute field %s for model %s in background. Last id %d",
                    task.field,
                    task.model,
                    task.last_id,
                )
                records = model.search(
                    [("id", "<", task.last_id)] if task.last_id else [],
                    limit=task.step,
                    order="id desc",
                )
                if not records:
                    task.state = "done"
                    cursor.commit()
                    break

                field = records._fields[task.field]
                self.env.add_to_compute(field, records)
                records.recompute()
                task.last_id = records[-1].id
                cursor.commit()

        return True


ori_add_to_compute = api.Environment.add_to_compute


def add_to_compute(self, field, records):
    if (
        "recompute.field" in self
        and len(records) > config.get("computed_fields_defer_threshold", 50000)
        and self.context.get("module")
        and not getattr(field, "precompute", False)
    ):
        _logger.info(
            "Deferring computation of field %s for model %s as there is %s records",
            field.name,
            records._name,
            len(records),
        )
        with self.norecompute():
            self["recompute.field"].create(
                {
                    "field": field.name,
                    "model": records._name,
                    "state": "todo",
                }
            )
    else:
        return ori_add_to_compute(self, field, records)


api.Environment.add_to_compute = add_to_compute
