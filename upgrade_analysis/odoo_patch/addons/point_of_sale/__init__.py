# flake8: noqa: B902
from odoo import api
from odoo.addons.point_of_sale.models import pos_config
from ...odoo_patch import OdooPatch


class PreInitHookPatch(OdooPatch):
    target = pos_config.PosConfig
    method_names = ["post_install_pos_localisation"]

    @api.model
    def post_install_pos_localisation(cr):
        """Do not configure twice pos_localisation"""
