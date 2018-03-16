# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import SUPERUSER_ID, api

from .models.module import PARAM_INSTALLED_CHECKSUMS
from .models.module_deprecated import PARAM_DEPRECATED


def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["ir.config_parameter"].set_param(PARAM_INSTALLED_CHECKSUMS, False)
    # TODO Remove from here when removing deprecated features
    env["ir.config_parameter"].set_param(PARAM_DEPRECATED, False)
    prefix = "module_auto_update.field_ir_module_module_checksum_%s"
    fields = env.ref(prefix % "dir") | env.ref(prefix % "installed")
    fields.with_context(_force_unlink=True).unlink()
