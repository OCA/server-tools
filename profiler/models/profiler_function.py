# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import api, fields, models
from odoo.exceptions import ValidationError

from ..tools import dynamic_profile

_logger = logging.getLogger(__name__)


class ProfilerFunction(models.Model):
    _name = "profiler.function"
    _description = "Profiled Function"
    _order = "name"

    name = fields.Char(required=True)
    python_path = fields.Char(
        required=True,
        index=True,
        help="Use module.function or module.Class.method",
    )
    sample_rate = fields.Float(
        default=0.05,
        help="Percentage of calls to profile (0.0 - 1.0)",
    )
    active = fields.Boolean(default=True)

    @api.constrains("python_path")
    def _check_python_path(self):
        for record in self:
            if not record.python_path:
                continue
            try:
                dynamic_profile.validate_path(record.python_path)
            except Exception as exc:
                raise ValidationError(
                    f"Invalid python path {record.python_path}: {exc}"
                ) from exc

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._update_registry()
        return records

    def write(self, vals):
        res = super().write(vals)
        if {"python_path", "sample_rate", "active"} & set(vals):
            self._update_registry()
        return res

    def unlink(self):
        res = super().unlink()
        self._update_registry()
        return res

    def _update_registry(self):
        if self.env.registry.ready:
            self._unregister_hook()
            self._register_hook()
            self.env.registry.registry_invalidated = True
        else:
            _logger.info("Registry not ready, skipping profiler patch update")

    def _register_hook(self):
        res = super()._register_hook()
        active_records = self.search([("active", "=", True)])
        dynamic_profile.patch_active_records(active_records)
        return res

    def _unregister_hook(self):
        res = super()._unregister_hook()
        for record in self.with_context(active_test=False).search([]):
            try:
                dynamic_profile.unpatch_path(record.python_path)
            except Exception as exc:
                _logger.warning(
                    "Unable to remove profile patch for %s: %s",
                    record.python_path,
                    exc,
                )
        return res
