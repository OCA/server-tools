# Copyright 2011-2015 Therp BV <https://therp.nl>
# Copyright 2016 Opener B.V. <https://opener.am>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os

from odoo import fields, models
from odoo.modules import get_module_path


class IrModuleModule(models.Model):
    _inherit = "ir.module.module"

    is_odoo_module = fields.Boolean(
        compute="_compute_is_odoo_module",
    )

    is_oca_module = fields.Boolean(compute="_compute_is_oca_module")

    def _compute_is_oca_module(self):
        for module in self:
            module.is_oca_module = "/OCA/" in module.website

    def _compute_is_odoo_module(self):
        for module in self:
            module_path = get_module_path(module.name)
            if not module_path:
                module.is_odoo_module = False
                continue
            absolute_repo_path = os.path.split(module_path)[0]
            x, relative_repo_path = os.path.split(absolute_repo_path)
            module.is_odoo_module = relative_repo_path == "addons"
