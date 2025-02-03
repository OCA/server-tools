# Copyright (C) 2019-Today: GRAP (<http://www.grap.coop/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
from odoo.tools.translate import _


class TestModule(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.IrModuleModule = cls.env["ir.module.module"]
        # Remove lib because it breaks tests in case of installation of modules with pip
        cls.env["ir.config_parameter"].set_param(
            "module_analysis.exclude_directories", "demo,test,tests,doc,description"
        )
        cls.IrModuleModule.cron_analyse_code()

    def test_installed_modules(self):
        installed_modules = self.IrModuleModule.search(
            [("state", "=", "installed"), ("name", "not like", "_test")]
        )
        for module in installed_modules:
            self.assertTrue(
                module.python_code_qty > 0
                or module.xml_code_qty > 0
                or module.js_code_qty > 0,
                _(
                    "module {} doesn't have code analysed defined, "
                    "whereas it is installed."
                ).format(module.name),
            )

    def test_uninstalled_modules(self):
        uninstalled_modules = self.IrModuleModule.search([("state", "!=", "installed")])
        for module in uninstalled_modules:
            self.assertTrue(
                module.python_code_qty == 0,
                _(
                    "module {} has python lines defined, whereas it is not installed."
                ).format(module.name),
            )

    def test_module_with_no_code(self):
        modules_with_no_code = self.IrModuleModule.search(
            [
                ("python_code_qty", "=", 0),
                ("xml_code_qty", "=", 0),
                ("js_code_qty", "=", 0),
            ]
        )
        for module in modules_with_no_code:
            self.assertTrue(
                module.state != "installed",
                _("module {} has no code but is marked as installed.").format(
                    module.name
                ),
            )

    def test_module_with_code(self):
        modules_with_code = self.IrModuleModule.search(
            [
                ("python_code_qty", ">", 0),
                ("xml_code_qty", ">", 0),
                ("js_code_qty", ">", 0),
            ]
        )
        for module in modules_with_code:
            self.assertTrue(
                module.state == "installed",
                _("module {} has code but is not marked as installed.").format(
                    module.name
                ),
            )
