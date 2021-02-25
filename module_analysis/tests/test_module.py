# Copyright (C) 2019-Today: GRAP (<http://www.grap.coop/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase, post_install


@post_install(True)
class TestModule(TransactionCase):

    def setUp(self):
        super().setUp()
        self.IrModuleModule = self.env['ir.module.module']

    def test_installed_modules(self):
        # Adding tests directories
        self.env.ref(
            'module_analysis.parameter_exclude_directories'
        ).value = "lib,demo,doc,description"
        installed_modules = self.IrModuleModule.search(
            [('state', '=', 'installed')])
        for module in installed_modules:
            # Analize again test modules
            if "test_" in module.name:
                module.button_analyse_code()
            self.assertTrue(
                module.python_code_qty > 0 or
                module.xml_code_qty > 0 or
                module.js_code_qty > 0,
                "module '%s' doesn't have code analysed defined, whereas it is"
                " installed." % (module.name))

    def test_uninstalled_modules(self):
        uninstalled_modules = self.IrModuleModule.search(
            [('state', '=', 'uninstalled')])
        for module in uninstalled_modules:
            self.assertTrue(
                module.python_code_qty == 0,
                "module '%s' has python lines defined, whereas it is"
                " not installed." % (module.name))
