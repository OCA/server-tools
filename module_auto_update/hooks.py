# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openerp import SUPERUSER_ID, api

from .models.module import PARAM_INSTALLED_CHECKSUMS
from .models.module_deprecated import PARAM_DEPRECATED


def install_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    # make sure migration to 9 does not enable deprecated features
    env["ir.config_parameter"].set_param(PARAM_DEPRECATED, '0')


def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["ir.config_parameter"].set_param(PARAM_INSTALLED_CHECKSUMS, False)
    env["ir.config_parameter"].set_param(PARAM_DEPRECATED, False)
