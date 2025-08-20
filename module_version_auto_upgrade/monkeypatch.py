import logging

import odoo
from odoo import modules, tools
from odoo.modules import loading
from odoo.modules.loading import load_module_graph

_logger = logging.getLogger(__name__)

_load_modules = loading.load_modules


def load_modules(registry, force_demo=False, status=None, update_module=False):
    # load_modules is a good spot to hook, because modules __init__.py are called
    # before this, but the registry is not yet fully loaded (so we avoid some weird
    # issues with .mapped() and computed fields).
    _logger.info("#######")
    modules_to_upgrade = get_upgradeable_modules(registry)
    if modules_to_upgrade:
        tools.config["update"].update({k: 1 for k in modules_to_upgrade})
        update_module = modules_to_upgrade or update_module
    return _load_modules(
        registry, force_demo=force_demo, status=status, update_module=update_module
    )


def get_upgradeable_modules(registry):
    with registry.cursor() as cr:
        if not odoo.modules.db.is_initialized(cr):
            # DB is not initialized, skip auto-upgrade
            return False
        if tools.config["update"] or tools.config["init"]:
            _logger.info(f"Checking database `{cr.dbname}` for modules to auto-upgrade")
            # do not trigger auto-upgrade if an upgrade/install is already requested
            return False

        _logger.info(f"Checking database `{cr.dbname}` for modules to auto-upgrade")

        # set up minimal environment
        graph = odoo.modules.graph.Graph()
        graph.add_module(cr, "base", [])
        env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
        loaded_modules, processed_modules = load_module_graph(
            env, graph, None, perform_checks=False, report=None, models_to_check=None
        )
        registry.setup_models(cr)

        # fetch installed modules
        Module = env["ir.module.module"]
        Module.update_list()
        modules = Module.search(
            [
                ("state", "in", ["installed"]),
                ("name", "not in", ["studio_customization"]),
            ],
        )

        # check for modules that need upgrading (and log them)
        to_upgrade = []
        for module in modules:
            if module["latest_version"] != module["installed_version"]:
                _logger.info(
                    f"Auto-upgrading module {module['name']} "
                    f"({module['latest_version']} -> {module['installed_version']})"
                )
                to_upgrade.append(module["name"])

        return to_upgrade


loading.load_modules = load_modules
modules.load_modules = load_modules
