# Copyright 2026 KMEE INFORMATICA LTDA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import os
import time

from odoo import api, models

_logger = logging.getLogger(__name__)

PARAM_MODELS = "base_field_trigger_warmup.models"
ENV_DISABLE = "ODOO_FIELD_TRIGGER_WARMUP"


class BaseFieldTriggerWarmup(models.AbstractModel):
    """Build the ORM compute dependency trees while the registry loads.

    The ORM resolves the transitive closure of compute triggers lazily, the
    first time a field is written. On models with many interdependent stored
    computed fields, that first write pays for the whole closure, so the first
    request served by each worker is much slower than the following ones. This
    model moves that cost to the registry load, where no user is waiting.
    """

    _name = "base.field.trigger.warmup"
    _description = "Field Trigger Tree Warmup"

    @api.model
    def _warmup_is_enabled(self):
        """Warmup is skipped in tests and when the env var is set to 0."""
        if os.environ.get(ENV_DISABLE, "1") == "0":
            return False
        return not self.env.registry.in_test_mode()

    @api.model
    def _warmup_model_names(self):
        """Model names to warm up.

        Read from the ``base_field_trigger_warmup.models`` system parameter: a
        comma separated list of model names, or ``*`` (the default) for every
        model in the registry. Narrowing it down is useful when only a few
        models are expensive and boot time matters.
        """
        param = (
            self.env["ir.config_parameter"].sudo().get_param(PARAM_MODELS, default="*")
            or ""
        ).strip()
        if param in ("", "*"):
            return list(self.env.registry)
        wanted = [name.strip() for name in param.split(",") if name.strip()]
        known, unknown = [], []
        for name in wanted:
            (known if name in self.env.registry else unknown).append(name)
        if unknown:
            _logger.warning(
                "%s lists unknown models, ignored: %s",
                PARAM_MODELS,
                ", ".join(unknown),
            )
        return known

    @api.model
    def _warmup_field_trigger_trees(self, model_names=None):
        """Build the trigger tree of every field of ``model_names``.

        Returns the number of fields whose tree was built. Failures on a single
        field are logged at debug level and skipped: a warmup must never be able
        to break the boot.
        """
        registry = self.env.registry
        # Private ORM API: guard it so an Odoo version that renames or drops it
        # degrades to a no-op instead of breaking the registry load.
        build_tree = getattr(registry, "get_field_trigger_tree", None)
        if build_tree is None:
            _logger.info(
                "This Odoo build has no Registry.get_field_trigger_tree, "
                "nothing to warm up"
            )
            return 0
        if model_names is None:
            model_names = self._warmup_model_names()
        count = 0
        for model_name in model_names:
            model = self.env.get(model_name)
            if model is None:
                continue
            for field in model._fields.values():
                try:
                    build_tree(field)
                except Exception:  # pylint: disable=except-pass
                    _logger.debug(
                        "Could not build the trigger tree of %s.%s",
                        model_name,
                        field.name,
                        exc_info=True,
                    )
                    continue
                count += 1
        return count

    def _register_hook(self):
        res = super()._register_hook()
        registry = self.env.registry
        # _register_hook runs once per model that defines it, and the registry
        # may be loaded more than once per process.
        if getattr(registry, "_field_trigger_warmup_done", False):
            return res
        registry._field_trigger_warmup_done = True
        if not self._warmup_is_enabled():
            return res
        start = time.time()
        count = self._warmup_field_trigger_trees()
        if count:
            _logger.info(
                "Warmed up %s field trigger trees in %.2fs",
                count,
                time.time() - start,
            )
        return res
