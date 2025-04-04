# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models

from ..register import register_vector


class IrModelFields(models.Model):
    _inherit = "ir.model.fields"

    ttype = fields.Selection(
        selection_add=[("vector", "Vector")],
        ondelete={"vector": "cascade"},
    )

    def init(self):
        # This method is called when the module is installed
        # at intallation time to register the field type in the database.
        # This is needed to ensure that the type is registered
        # where runnig tests at installation time.
        res = super().init()
        register_vector(self.env.cr)
        return res

    def _register_hook(self):
        # This method is called when the module is loaded to
        # register the field type in the database.
        res = super()._register_hook()
        register_vector(self.env.cr)
        return res
