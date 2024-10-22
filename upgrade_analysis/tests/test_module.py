from odoo.tests import common, tagged


@tagged("post_install", "-at_install")
class TestUpgradeAnalysis(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.IrModuleModule = self.env["ir.module.module"]
        self.website_module = self.IrModuleModule.search([("name", "=", "website")])
        self.sale_module = self.IrModuleModule.search([("name", "=", "sale")])
        self.upgrade_analysis = self.IrModuleModule.search(
            [("name", "=", "upgrade_analysis")]
        )

    def test_upgrade_install_wizard(self):
        InstallWizard = self.env["upgrade.install.wizard"]
        wizard = InstallWizard.create({})

        wizard.select_odoo_modules()
        self.assertTrue(
            self.website_module.id in wizard.module_ids.ids,
            "Select Odoo module should select 'product' module",
        )
        wizard.select_other_modules()
        self.assertFalse(
            self.website_module.id in wizard.module_ids.ids,
            "Select Other module should not select 'product' module",
        )
        wizard.unselect_modules()
        self.assertEqual(
            wizard.module_ids.ids, [], "Unselect module should clear the selection"
        )
        # For the time being, tests doens't call install_modules() function
        # because installing module in a test context will execute the test
        # of the installed modules, raising finally an error:

        # TypeError: Many2many fields ir.actions.server.partner_ids and
        # ir.actions.server.partner_ids use the same table and columns
