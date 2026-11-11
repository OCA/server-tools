# Copyright (C) 2019-Today: GRAP (<http://www.grap.coop/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestModule(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.IrModuleModule = cls.env["ir.module.module"]
        # Remove lib because it breaks tests in case of installation of modules with
        # pip
        cls.env["ir.config_parameter"].set_param(
            "module_analysis.exclude_directories", "demo,test,tests,doc,description"
        )

    def test_installed_modules(self):
        installed_modules = self.IrModuleModule.search(
            [("state", "=", "installed"), ("name", "not like", "_test")]
        )
        for module in installed_modules:
            module.button_analyse_code()
            self.assertTrue(
                (
                    module.python_code_qty > 0
                    or module.xml_code_qty > 0
                    or module.js_code_qty > 0
                    or module.css_code_qty > 0
                    or module.scss_code_qty > 0
                    or module.module_type_id
                ),
                f"module {module.name} doesn't have code analysed defined, "
                "whereas it is installed.",
            )

    def test_uninstalled_modules(self):
        uninstalled_modules = self.IrModuleModule.search([("state", "!=", "installed")])
        for module in uninstalled_modules:
            self.assertTrue(
                module.python_code_qty == 0,
                f"module {module.name} has python lines defined, "
                "whereas it is not installed.",
            )
