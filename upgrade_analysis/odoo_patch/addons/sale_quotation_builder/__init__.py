# flake8: noqa: B902
from odoo.addons import sale_quotation_builder
from ...odoo_patch import OdooPatch


class PreInitHookPatch(OdooPatch):
    target = sale_quotation_builder
    method_names = ["_pre_init_sale_quotation_builder"]

    def _pre_init_sale_quotation_builder(cr):
        """Don't pre-create existing columns on reinstall"""
