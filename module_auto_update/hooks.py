# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import SUPERUSER_ID, api

from .models.module import PARAM_INSTALLED_CHECKSUMS


def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["ir.config_parameter"].set_param(PARAM_INSTALLED_CHECKSUMS, False)
