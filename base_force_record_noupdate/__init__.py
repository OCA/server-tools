from . import models


def post_init_hook(cr, registry):
    """Configure a list of models having ``force_noupdate`` set by default"""
    from odoo import SUPERUSER_ID, api

    env = api.Environment(cr, SUPERUSER_ID, {})
    mods = env["ir.model"].sudo()
    for model_name in [
        "res.lang",
        "ir.rule",
        "ir.model.access",
        "res.groups",
        "mail.template",
        "res.users.role",  # Don't care if the module providing this is installed
    ]:
        mod = env["ir.model"]._get(model_name)
        if mod and mod.exists():
            mods |= mod
    if mods:
        mods.write({"force_noupdate": True})
