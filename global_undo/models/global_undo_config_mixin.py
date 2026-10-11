# Copyright 2026 Pol Reig <pol.reig@qubiq.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class GlobalUndoConfigMixin(models.AbstractModel):
    """Configuration whose every change has to reach a cache somewhere.

    Both configuration models are read on hot paths and cached, so no edit may
    be allowed to go unnoticed.
    """

    _name = "global.undo.config.mixin"
    _description = "Global Undo Configuration Mixin"

    # CRUD methods

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._gu_config_changed()
        return records

    def write(self, vals):
        result = super().write(vals)
        self._gu_config_changed()
        return result

    def unlink(self):
        self._gu_config_changed()
        return super().unlink()

    # Business methods

    def _gu_config_changed(self):
        raise NotImplementedError
