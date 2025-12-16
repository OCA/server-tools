# Copyright 2025 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import logging
from functools import reduce
from itertools import groupby

from odoo import api, fields, models
from odoo.exceptions import Warning as UserError
from odoo.tools import config
from odoo.tools.translate import _

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
        # Group tasks by compute method to avoid computing multifields computes multiple times

        def group_key(task):
            return task.model, str(self.env[task.model]._fields[task.field].compute)

        model_tasks = groupby(
            self.sorted(key=group_key),
            group_key,
        )
        for (model, _compute_fun), tasks in model_tasks:
            tasks = reduce(lambda x, y: x | y, tasks)
            fields = set(tasks.mapped("field"))
            last_id = max(tasks.mapped("last_id"), default=None)
            step = min(tasks.mapped("step"))

            while True:
                _logger.info(
                    "Recompute fields %s for model %s in background. Last id %d",
                    fields,
                    model,
                    last_id,
                )
                records = self.env[model].search(
                    [("id", "<", last_id)] if last_id else [],
                    limit=step,
                    order="id desc",
                )
                if not records:
                    tasks.state = "done"
                    self.env.cr.commit()  # pylint: disable=E8102
                    break
                for field in fields:
                    field_ = records._fields[field]
                    self.env.add_to_compute(field_, records)

                records.flush_recordset()
                last_id = records[-1].id
                tasks.last_id = last_id
                self.env.cr.commit()  # pylint: disable=E8102

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
