# Copyright (C) 2021 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import os

from odoo import modules
from odoo.tools import config

_logger = logging.getLogger(__name__)
_original_load_manifest = modules.module.load_manifest


def _get_modules_dict_auto_install_config(config_value):
    """Given a configuration parameter name, return a dict of
    {module_name: modules_list or False}

    if the odoo.cfg file contains

        modules_auto_install_enabled =
            web_responsive:web,
            base_technical_features:,
            point_of_sale:sale/purchase,
            account_usability

    >>> split_strip('modules_auto_install_enabled')
    {
        'web_responsive': ['web'],
        'base_technical_features': [],
        'point_of_sale': ['sale', 'purchase'],
        'account_usability': False,
    }


    """
    res = {}
    config_value = (config_value or "").strip(" ,")
    config_list = [x.strip() for x in config_value.split(",")]
    for item in config_list:
        if ":" in item:
            res[item.split(":")[0]] = (
                item.split(":")[1] and item.split(":")[1].split("/") or []
            )
        else:
            res[item] = True
    return res


def _overload_load_manifest(module, mod_path=None):

    res = _original_load_manifest(module, mod_path=None)
    auto_install = res.get("auto_install", False)

    modules_auto_install_enabled_dict = _get_modules_dict_auto_install_config(
        config.get(
            "modules_auto_install_enabled",
            os.environ.get("ODOO_MODULES_AUTO_INSTALL_ENABLED"),
        )
    )
    modules_auto_install_disabled_dict = _get_modules_dict_auto_install_config(
        config.get(
            "modules_auto_install_disabled",
            os.environ.get("ODOO_MODULES_AUTO_INSTALL_DISABLED"),
        )
    )

    if auto_install and module in modules_auto_install_disabled_dict.keys():
        _logger.info("Module '%s' has been marked as NOT auto installable." % module)
        res["auto_install"] = False

    if not auto_install and module in modules_auto_install_enabled_dict.keys():
        specific_dependencies = modules_auto_install_enabled_dict.get(module)
        if type(specific_dependencies) is bool:
            # Classical case
            _logger.info("Module '%s' has been marked as auto installable." % module)
            res["auto_install"] = set(res["depends"])
        else:
            if specific_dependencies:
                _logger.info(
                    "Module '%s' has been marked as auto installable if '%s' are installed"
                    % (module, ",".join(specific_dependencies))
                )
            else:
                _logger.info(
                    "Module '%s' has been marked as auto installable in ALL CASES."
                    % module
                )

            res["auto_install"] = set(specific_dependencies)

    return res


def post_load():
    _logger.info("Applying patch module_change_auto_intall ...")
    modules.module.load_manifest = _overload_load_manifest
    modules.load_manifest = _overload_load_manifest
