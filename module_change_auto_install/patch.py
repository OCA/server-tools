# Copyright (C) 2021 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import configparser
import logging
import os

from odoo.modules.module import Manifest
from odoo.tools import config

_logger = logging.getLogger(__name__)
_original_init = Manifest.__init__


def _get_modules_dict_auto_install_config(config_value):
    """Given a configuration parameter name, return a dict of
    {module_name: modules_list or False}

    if the odoo.cfg file contains
        [module_change_auto_install]
        modules_enabled =
            web_responsive:web,
            base_technical_features:,
            point_of_sale:sale/purchase,
            account_usability

    >>> split_strip('modules_enabled')
    {
        'web_responsive': ['web'],
        'base_technical_features': [],
        'point_of_sale': ['sale', 'purchase'],
        'account_usability': False,
    }


    """
    res = {}
    config_value = (config_value or "").strip(" ,")
    if config_value:
        config_list = [x.strip() for x in config_value.split(",")]
        for item in config_list:
            if ":" in item:
                res[item.split(":")[0]] = (
                    item.split(":")[1] and item.split(":")[1].split("/") or []
                )
            else:
                res[item] = True
    return res


def _get_modules_auto_install_enabled_dict():
    return _get_modules_dict_auto_install_config(
        config.get(
            "module_change_auto_install.modules_enabled",
            os.environ.get("ODOO_MODULES_AUTO_INSTALL_ENABLED"),
        )
    )


def _get_modules_auto_install_disabled_dict():
    return _get_modules_dict_auto_install_config(
        config.get(
            "module_change_auto_install.modules_disabled",
            os.environ.get("ODOO_MODULES_AUTO_INSTALL_DISABLED"),
        )
    )


def _get_auto_install_flag(self):
    modules_auto_install_enabled_dict = _get_modules_auto_install_enabled_dict()
    modules_auto_install_disabled_dict = _get_modules_auto_install_disabled_dict()
    auto_install = self._Manifest__manifest_cached["auto_install"]
    module = self.name

    if auto_install and module in modules_auto_install_disabled_dict.keys():
        _logger.info(f"Module '{module}' has been marked as NOT auto installable.")
        return False

    if not auto_install and module in modules_auto_install_enabled_dict.keys():
        specific_dependencies = modules_auto_install_enabled_dict.get(module)
        if isinstance(specific_dependencies, bool):
            # Classical case
            _logger.info(f"Module '{module}' has been marked as auto installable.")
            return set(self._Manifest__manifest_cached["depends"])
        else:
            if specific_dependencies:
                _logger.info(
                    "Module '{}' has been marked as auto installable if '{}' "
                    "are installed".format(module, ",".join(specific_dependencies))
                )
            else:
                _logger.info(
                    f"Module '{module}' has been marked as auto installable in "
                    f"ALL CASES."
                )

            return set(specific_dependencies)
    return auto_install


def _patched_init(self, *, path: str, manifest_content: dict):
    _original_init(self, path=path, manifest_content=manifest_content)
    # Post-process before cached_property kicks in
    self.auto_install = _get_auto_install_flag(self)
    if "auto_install" in self._Manifest__manifest_cached:
        self._Manifest__manifest_cached["auto_install"] = self.auto_install


def _load_module_change_auto_install_options(rcfile):
    """Load custom [module_change_auto_install] section into config."""
    cp = configparser.ConfigParser()
    cp.read([rcfile])

    if cp.has_section("module_change_auto_install"):
        for key, value in cp.items("module_change_auto_install"):
            # Store with prefix to avoid collisions
            config[f"module_change_auto_install.{key}"] = value
            _logger.debug("Loaded custom option %s=%s", key, value)


def post_load():
    _logger.info("Applying patch module_change_auto_install ...")
    Manifest.__init__ = _patched_init
    rcfile = config.get("config")
    if rcfile:
        _load_module_change_auto_install_options(rcfile)
