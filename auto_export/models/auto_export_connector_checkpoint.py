# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

from odoo.addons.connector.models.checkpoint import (
    add_checkpoint as original_add_checkpoint,
)


class AutoExportConnectorCheckpoint(models.Model):
    _inherit = "connector.checkpoint"
    description = fields.Text(string="Description",)


def add_checkpoint(
    env, model_name, record_id, backend_model_name, backend_id, description
):
    checkpoint = original_add_checkpoint(
        env, model_name, record_id, backend_model_name, backend_id
    )
    checkpoint.description = description
    return checkpoint
