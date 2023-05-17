import logging
from threading import current_thread

from odoo import SUPERUSER_ID, api
from odoo.modules.registry import Registry

from .... import upgrade_log
from ...odoo_patch import OdooPatch

_logger = logging.getLogger(__name__)


class RegistryPatch(OdooPatch):
    target = Registry
    method_names = ["init_models"]

    def init_models(self, cr, model_names, context, install=True):
        if "module" in context:
            module_name = context["module"]
            _logger.debug("Logging models of module %s", module_name)
            upg_registry = current_thread()._upgrade_registry
            local_registry = {}
            env = api.Environment(cr, SUPERUSER_ID, {})
            for model in env.values():
                if not model._auto:
                    continue
                upgrade_log.log_model(model, local_registry)
            upgrade_log.compare_registries(
                cr, context["module"], upg_registry, local_registry
            )

        return RegistryPatch.init_models._original_method(
            self, cr, model_names, context, install=install
        )
