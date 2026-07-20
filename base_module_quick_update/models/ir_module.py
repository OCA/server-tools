# Copyright (C) 2026 XXP
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import _, models
from odoo.addons.base.models.ir_module import ACTION_DICT, assert_log_admin_access
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class IrModuleModule(models.Model):
    _inherit = "ir.module.module"

    @assert_log_admin_access
    def button_quick_upgrade(self):
        """
        Upgrade the selected modules. Unlike the standard method, this mode
        does not automatically upgrade other modules that depend on them (downstream).
        However, any missing required dependencies (upstream) will still be installed
        to ensure the module upgrades correctly.
        """

        if not self:
            return
        self.update_list()

        for module in self:
            if module.state not in ("installed", "to upgrade"):
                raise UserError(
                    _("Can not upgrade module '%s'. It is not installed.")
                    % (module.name,)
                )
            if self.get_module_info(module.name).get("installable", True):
                self.check_external_dependencies(module.name, "to upgrade")

        self.write({"state": "to upgrade"})

        to_install = []
        for module in self:
            if not self.get_module_info(module.name).get("installable", True):
                continue
            for dep in module.dependencies_id:
                if dep.state == "unknown":
                    raise UserError(
                        _(
                            "You try to upgrade the module %s that depends on "
                            "the module: %s.\nBut this module is not available "
                            "in your system."
                        )
                        % (module.name, dep.name)
                    )
                if dep.state == "uninstalled":
                    to_install += self.search([("name", "=", dep.name)]).ids

        self.browse(to_install).button_install()
        return dict(ACTION_DICT, name=_("Apply Schedule Upgrade"))

    @assert_log_admin_access
    def button_immediate_quick_upgrade(self):
        """Immediately upgrade the selected module(s) without cascading to the
        installed dependents; returns the next res.config action to execute.
        """
        _logger.info(
            "User #%d triggered quick module upgrade", self.env.uid
        )
        return self._button_immediate_function(
            self.env.registry[self._name].button_quick_upgrade
        )
