# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openerp import api, models


class ModuleUpgrade(models.TransientModel):
    _inherit = 'base.module.upgrade'

    @api.model
    def get_module_list(self):
        """Set modules to upgrade searching by their dir checksum."""
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
        """Make a fully automated addon upgrade."""
        # Compute updates by checksum when called in @api.model fashion
        if not self:
            self.get_module_list()
        Module = self.env["ir.module.module"]
        # Get every addon state before updating
        pre_states = {addon.name: addon.state for addon in Module.search([])}
        # Perform upgrade, possibly in an addon graph that has no notion of
        # ``module_auto_update`` and skips its triggers
        result = super(ModuleUpgrade, self).upgrade_module()
        # Update addon checksum if state changed
        Module.invalidate_cache()
        for addon in Module.search([]):
            if addon.state != pre_states.get(addon.name):
                # This triggers the write hook that should have been triggered
                # when the module was [un]installed/updated in the limited
                # module graph inside above call to super(), and updates its
                # dir checksum as needed
                addon.latest_version = addon.latest_version
        return result
