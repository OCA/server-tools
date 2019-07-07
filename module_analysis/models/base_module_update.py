# Copyright (C) 2019-Today: GRAP (<http://www.grap.coop/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class BaseModuleUpdate(models.TransientModel):
    _inherit = 'base.module.update'

    analyze_installed_modules = fields.Boolean(
        string='Analyze Installed Modules', default=True)

    @api.multi
    def update_module(self):
        return super(BaseModuleUpdate, self.with_context(
            analyze_installed_modules=self.analyze_installed_modules)
        ).update_module()
