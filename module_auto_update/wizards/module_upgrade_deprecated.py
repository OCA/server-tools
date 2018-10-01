# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from odoo import api, models

from ..models.module_deprecated import PARAM_DEPRECATED

_logger = logging.getLogger(__name__)


class ModuleUpgrade(models.TransientModel):
    _inherit = 'base.module.upgrade'

    @api.model
    def _autoupdate_deprecated(self):
        """Know if we should enable deprecated features."""
        deprecated = (
            self.env["ir.config_parameter"].get_param(PARAM_DEPRECATED))
        if deprecated is False:
            # Enable deprecated features if this is the 1st automated update
            # after the version that deprecated them (X.Y.2.0.0)
            own_module = self.env["ir.module.module"].search([
                ("name", "=", "module_auto_update"),
            ])
            try:
                if own_module.latest_version.split(".")[2] == "1":
                    deprecated = "1"
            except AttributeError:
                pass  # 1st install, there's no latest_version
        return deprecated == "1"

    @api.model
    def get_module_list(self):
        """Set modules to upgrade searching by their dir checksum."""
        if self._autoupdate_deprecated():
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
        if self._autoupdate_deprecated():
            _logger.warning(
                "You are possibly using an unsupported upgrade system; "
                "set '%s' system parameter to '0' and start calling "
                "`env['ir.module.module'].upgrade_changed_checksum()` from "
                "now on to get rid of this message. See module's README's "
                "Known Issues section for further information on the matter."
            )
            # Compute updates by checksum when called in @api.model fashion
            self.env.cr.autocommit(True)  # Avoid transaction lock
            if not self:
                self.get_module_list()
            Module = self.env["ir.module.module"]
            # Get every addon state before updating
            pre_states = {addon["name"]: addon["state"] for addon
                          in Module.search_read([], ["name", "state"])}
        # Perform upgrades, possibly in a limited graph that excludes me
        result = super(ModuleUpgrade, self).upgrade_module()
        if self._autoupdate_deprecated():
            self.env.cr.autocommit(False)
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
                        # triggered when the module was [un]installed/updated
                        # in the limited module graph inside above call to
                        # super(), and updates its dir checksum as needed
                        addon.latest_version = addon.latest_version
        return result
