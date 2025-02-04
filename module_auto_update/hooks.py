# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from .models.module import PARAM_INSTALLED_CHECKSUMS


def uninstall_hook(env):
    env["ir.config_parameter"].set_param(PARAM_INSTALLED_CHECKSUMS, False)
