# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models


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
    def upgrade_module(self):
        """Make a fully automated addon upgrade."""
        Module = self.env["ir.module.module"]
        # Update the modules list to resolve new dependencies
        Module.update_list()
        # Compute updates by checksum when called in @api.model fashion
        if not self:
            self.get_module_list()
        # Get every addon state before updating
        pre_states = {addon["name"]: addon["state"]
                      for addon in Module.search_read([], ["name", "state"])}
        # Perform upgrades, possibly in a limited graph that excludes me
        result = super(ModuleUpgrade, self).upgrade_module()
        # Reload environments, anything may have changed
        self.env.clear()
        # Update addons checksum if state changed and I wasn't uninstalled
        own = Module.search_read(
            [("name", "=", "module_auto_update")],
            ["state"],
            limit=1)
        if own and own[0]["state"] != "uninstalled":
            for addon in Module.search([]):
                if addon.state != pre_states.get(addon.name):
                    # Trigger the write hook that should have been
                    # triggered when the module was [un]installed/updated in
                    # the limited module graph inside above call to super(),
                    # and updates its dir checksum as needed
                    addon.latest_version = addon.latest_version
        return result
