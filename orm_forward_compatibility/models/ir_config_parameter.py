# Copyright 2026 Camptocamp SA
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).
from odoo import models
from odoo.tools import str2bool


class IrConfigParameter(models.Model):
    _inherit = "ir.config_parameter"

    def get_str(self, key, default=""):
        value = self.get_param(key)
        return default if value is False else str(value)

    def get_int(self, key, default=0):
        value = self.get_param(key)
        if value is False:
            return default
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def get_float(self, key, default=0.0):
        value = self.get_param(key)
        if value is False:
            return default
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def get_bool(self, key, default=False):
        value = self.get_param(key)
        return default if value is False else str2bool(value, default)
