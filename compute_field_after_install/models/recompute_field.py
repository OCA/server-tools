# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import logging

from openerp import api, fields, models
from openerp.exceptions import Warning as UserError
from openerp.tools.translate import _

from odoo.tools import config

_logger = logging.getLogger(__name__)


class RecomputeField(models.Model):
    _name = "recompute.field"
    _description = "Recompute Field"

    model = fields.Char(required=True)
    field = fields.Char(required=True)
    last_id = fields.Integer(
        string="Last ID", help="Last record ID on which computing have been executed"
    )
    step = fields.Integer(required=True, default=1000, help="Recomputing batch size.")
    state = fields.Selection(
        [
            ("todo", "Todo"),
            ("done", "Done"),
        ]
    )

    @api.model
    def _run_all(self):
        return self.search([("state", "=", "todo")]).run()

    def run(self):
        for task in self:
            cursor = self.env.cr
            offset = 0
            model = self.env[task.model]
            if task.last_id:
                domain = [("id", ">", task.last_id)]
            else:
                domain = []
            if task.step <= 0:
                raise UserError(_("Step must be upper than 0"))
            else:
                limit = task.step
            while True:
                _logger.info(
                    "Recompute field %s for model %s in background. Offset %s",
                    task.field,
                    task.model,
                    offset,
                )
                records = model.search(domain, limit=limit, offset=offset, order="id")
                if not records:
                    break
                offset += limit
                field = records._fields[task.field]
                self.env.add_to_compute(field, records)
                records.recompute()
                task.last_id = records[-1].id
                cursor.commit()
            task.state = "done"
            cursor.commit()
        return True


ori_add_to_compute = api.Environment.add_to_compute


def add_to_compute(self, field, records):
    if (
        "recompute.field" in self
        and len(records) > config.get("differ_recomputed_field_size", 50000)
        and self.context.get("module")
    ):
        _logger.info(
            "Differs recomputation of field %s for model %s as there is %s records",
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
