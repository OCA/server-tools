from copy import deepcopy

from odoo.tests import common, tagged
from odoo.tools import mute_logger

from .. import compare, upgrade_log
from ..odoo_patch.odoo_patch import OdooPatch


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
        # New patch avoids to reinstall already installed modules, so this will fail
        # wizard.select_oca_modules()
        # self.assertTrue(
        #     self.upgrade_analysis.id in wizard.module_ids.ids,
        #     "Select OCA module should select 'upgrade_analysis' module",
        # )

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

    def test_odoo_patch(self):
        """
        Test the patched versions of Odoo's base functions
        """
        self.assertFalse(
            self.env["upgrade.record"].search(
                [
                    ("name", "=", "base.constraint_ir_module_module_name_uniq"),
                    ("type", "=", "xmlid"),
                ]
            )
        )
        # Mute Odoo's noisy model patch snitcher
        with mute_logger("odoo.tests.common"), OdooPatch():
            self.env["ir.model.constraint"]._reflect_model(self.IrModuleModule)
        self.assertTrue(
            self.env["upgrade.record"].search(
                [
                    ("name", "=", "base.constraint_ir_module_module_name_uniq"),
                    ("type", "=", "xmlid"),
                ]
            )
        )

    def test_field_comparison(self):
        """
        Test we compare fields correctly
        """
        registry = {}
        upgrade_log.log_model(self.env["upgrade.analysis"], registry)
        upgrade_log.compare_registries(self.env.cr, "upgrade_analysis", {}, registry)
        old_fields = self.env["upgrade.record"].field_dump()
        new_fields = deepcopy(old_fields)

        def assertInFieldComparison(comparison, field, needle):
            self.assertIn(
                needle,
                "".join(
                    line
                    for line in comparison["upgrade_analysis"]
                    if f"/ {field} (" in line
                ),
            )

        state_field = [
            field
            for field in new_fields
            if field["field"] == "state" and field["model"] == "upgrade.analysis"
        ][0]

        state_field["selection_keys"] = "['done', 'new']"
        comparison = compare.compare_sets(old_fields, new_fields)
        assertInFieldComparison(comparison, "state", "added: [new]")
        assertInFieldComparison(comparison, "state", "removed: [draft]")

        state_field["selection_keys"] = "['done', 'draft', 'new']"
        comparison = compare.compare_sets(old_fields, new_fields)
        assertInFieldComparison(comparison, "state", "added: [new]")
        assertInFieldComparison(comparison, "state", "most likely nothing to do")
        with self.assertRaises(AssertionError):
            assertInFieldComparison(comparison, "state", "removed")

        state_field["selection_keys"] = "function"
        comparison = compare.compare_sets(old_fields, new_fields)
        with self.assertRaises(AssertionError):
            assertInFieldComparison(comparison, "state", "added: [new]")
        with self.assertRaises(AssertionError):
            assertInFieldComparison(comparison, "state", "removed")
