# Copyright (C) 2021 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import modules
from odoo.tools import config

_logger = logging.getLogger(__name__)
_original_load_information_from_description_file = (
    modules.module.load_information_from_description_file
)


def split_strip(s):
    """Split string and strip each component sep by comma

    >>> split_strip("foo, bar,")
    ['foo', 'bar']

    >>> split_strip("")
    []

    >>> split_strip(None)
    []
    """
    s = (s or "").strip(" ,")
    if not s:
        return []
    return [x.strip() for x in s.split(",")]


def _overload_load_information_from_description_file(module, mod_path=None):
    res = _original_load_information_from_description_file(module, mod_path=None)
    auto_install = res.get("auto_install", False)

    modules_auto_install_enabled = split_strip(
        config.get("modules_auto_install_enabled")
    )
    modules_auto_install_disabled = split_strip(
        config.get("modules_auto_install_disabled")
    )

    if auto_install and module in modules_auto_install_disabled:
        _logger.info("Module '%s' has been marked as not auto installable." % module)
        res["auto_install"] = False

    if not auto_install and module in modules_auto_install_enabled:
        _logger.info("Module '%s' has been marked as auto installable." % module)
        res["auto_install"] = True

    return res


def post_load():
    _logger.info("Applying patch module_change_auto_intall")
    modules.module.load_information_from_description_file = (
        _overload_load_information_from_description_file
    )
    modules.load_information_from_description_file = (
        _overload_load_information_from_description_file
    )
