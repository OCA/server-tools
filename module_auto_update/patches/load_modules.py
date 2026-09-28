# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import logging
import os

from odoo import SUPERUSER_ID, api, modules
from odoo.modules import loading
from odoo.modules.loading import load_module_graph
from odoo.tools import config, parse_version

_load_modules = loading.load_modules
_logger = logging.getLogger(__name__)


def load_modules(registry, force_demo=False, status=None, update_module=False):
    # load_modules is a good spot to hook, because modules __init__.py are called
    # before this, but the registry is not yet fully loaded (so we avoid some weird
    # issues with .mapped() and computed fields).
    modules_to_update = get_updateable_modules(registry)
    if modules_to_update:
        config["update"].update({k: 1 for k in modules_to_update})
        update_module = modules_to_update or update_module
    return _load_modules(
        registry, force_demo=force_demo, status=status, update_module=update_module
    )


def get_updateable_modules(registry):
    with registry.cursor() as cr:
        if not modules.db.is_initialized(cr):
            _logger.debug("Skipping auto-update; database not initialized")
            return False

        if config["init"]:
            _logger.debug("Skipping auto-update; install requested")
            return False

        _logger.debug("Checking database `%s` for modules to auto-update", cr.dbname)

        # set up minimal environment
        graph = modules.graph.Graph()
        graph.add_module(cr, "base", [])
        env = api.Environment(cr, SUPERUSER_ID, {})
        load_module_graph(
            env, graph, None, perform_checks=False, report=None, models_to_check=None
        )
        registry.setup_models(cr)

        # fetch installed modules
        Module = env["ir.module.module"]
        Module.update_list()

        # TODO Load from config: modules_auto_update_disabled
        no_update = ["studio_customization"]

        # check for modules that need upgrading (and log them)
        to_update = []
        for module in Module.search(
            [
                ("state", "=", "installed"),
                ("name", "not in", no_update),
            ],
        ):
            # Per odoo/addons/base/models/ir_module.py
            # installed_version refers the latest version (the one on disk)
            # latest_version refers the installed version (the one in database)
            if parse_version(module["latest_version"]) < parse_version(
                module["installed_version"]
            ):
                _logger.info(
                    f"Auto-upgrading module {module['name']} "
                    f"({module['latest_version']} -> {module['installed_version']})"
                )
                to_update.append(module["name"])

        return to_update


def patch_load_modules():
    if config.get(
        "module_auto_update",
        os.environ.get("ODOO_MODULE_AUTO_UPDATE"),
    ):
        loading.load_modules = load_modules
        modules.load_modules = load_modules
        _logger.info("patched load_modules")
