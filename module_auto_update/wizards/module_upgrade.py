# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openerp import api, models


class ModuleUpgrade(models.TransientModel):
    _inherit = 'base.module.upgrade'

    @api.model
    def get_module_list(self):
        Module = self.env["ir.module.module"]
        installed_modules = Module.search([('state', '=', 'installed')])
        upgradeable_modules = installed_modules.filtered(
            lambda r: r.checksum_dir != r.checksum_installed,
        )
        upgradeable_modules.button_upgrade()
        return super(ModuleUpgrade, self).get_module_list()

    @api.multi
    def upgrade_module_cancel(self):
        return super(
            ModuleUpgrade,
            self.with_context(retain_checksum_installed=True),
        ).upgrade_module_cancel()

    @api.multi
    def upgrade_module(self):
        # Compute updates by checksum when called in @api.model fashion
        if not self:
            self.get_module_list()
        # Get base adddon status before updating
        base = self.env["ir.module.module"].search([("name", "=", "base")])
        pre_state = base.state
        result = super(ModuleUpgrade, self).upgrade_module()
        # Update base addon checksum if its state changed
        base.invalidate_cache()
        if base.state != pre_state:
            # This triggers the write hook that should have been triggered
            # when the module was [un]installed/updated in the base-only
            # module graph inside above call to super(), and updates its
            # dir checksum as needed
            base.latest_version = base.latest_version
        return result
