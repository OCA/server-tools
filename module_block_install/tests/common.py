# Copyright 2026 Trobz
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tools import mute_logger


class ModuleBlockInstallCommon:
    def setUp(self):
        super().setUp()
        # The dummy modules have no manifest on disk: Odoo warns about it
        # whenever their dependencies or manifest are read.
        self.enterContext(mute_logger("odoo.modules.module"))

    @classmethod
    def _create_dummy_modules(cls, env):
        """Create module records that do not exist on disk, so module
        operations can be tested without touching real addons."""
        Module = env["ir.module.module"]
        cls.mod_uninstalled = Module.create(
            {"name": "module_block_install_dummy_new", "state": "uninstalled"}
        )
        cls.mod_installed = Module.create(
            {"name": "module_block_install_dummy_installed", "state": "installed"}
        )
        # Installed module with a new, not yet installed dependency: the
        # project bundle case.
        cls.mod_bundle = Module.create(
            {"name": "module_block_install_dummy_bundle", "state": "installed"}
        )
        env["ir.module.module.dependency"].create(
            {"module_id": cls.mod_bundle.id, "name": cls.mod_uninstalled.name}
        )
