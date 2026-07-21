from copy import deepcopy
from unittest.mock import patch

from lxml import etree

from odoo.tests import common, tagged

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
        with OdooPatch():
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

    def test_xml_comparison(self):
        """
        Test corner cases in noupdate_changes
        """
        # x2many field that was set in noupdate data in previous version,
        # but not mentioned in noupdate data of current version
        diff = self.env["upgrade.analysis"]._get_xml_diff(
            {},
            {
                "some_xmlid": etree.fromstring(
                    """
                    <record id="some_xmlid" model="upgrade.install.wizard">
                        <field
                            name="module_ids"
                            eval="[Command.set([ref('base.module_web')])]"
                        />
                        <field name="display_name">some name</field>
                    </record>
                    """
                ),
            },
            {},
            {
                "some_xmlid": etree.fromstring(
                    """
                    <record id="some_xmlid" model="upgrade.install.wizard" />
                    """
                ),
            },
            "upgrade_analysis",
        )
        self.assertIn('<field name="module_ids" eval="None"/>', diff)
        self.assertIn('<field name="display_name"/>', diff)

    def test_analyze(self):
        """
        Test a full analysis run.
        For the time being, only xmlid related functionality is tested.

        The record is detected as renamed from ``other_module`` to
        ``upgrade_analysis`` and the generated ``noupdate_changes.xml``
        exercises the discarded-field handling:

        - ``name``: value changed, so it is written;
        - ``port``: dropped, and the value a fresh install gives (its default)
          differs from the previous one, so a reset is written;
        - ``username``: dropped, but the default equals the previous value, so
          nothing is written;
        - ``database``: dropped, but its field is (patched to be) declared in a
          module the current one does not depend on, so it is left untouched.
        """
        analysis = self.env["upgrade.analysis"].create(
            {
                "config_id": self.env["upgrade.comparison.config"]
                .create(
                    {
                        "database": self.env.cr.dbname,
                    }
                )
                .id,
            }
        )
        upgrade_analysis_version = (
            self.env["ir.module.module"]
            .search([("name", "=", "upgrade_analysis")])
            .latest_version
        )

        self.env["upgrade.record"].create(
            {
                "name": "upgrade_analysis.test_noupdate_xmlid",
                "mode": "create",
                "type": "xmlid",
                "module": "upgrade_analysis",
                "model": "upgrade.comparison.config",
                "noupdate": True,
            }
        )

        class RemoteUpgradeRecord:
            _records = {
                1: {
                    "name": "other_module.test_noupdate_xmlid",
                    "mode": "create",
                    "type": "xmlid",
                    "module": "other_module",
                    "prefix": "other_module",
                    "model": "upgrade.comparison.config",
                    "noupdate": True,
                    "suffix": "test_noupdate_xmlid",
                },
            }

            def search(self, domain):
                if domain == [("type", "=", "xmlid")]:
                    return [
                        _id
                        for _id, vals in self._records.items()
                        if vals["type"] == "xmlid"
                    ]
                return []

            def read(self, ids, fields):  # pylint: disable=method-required-super
                return [
                    {field: record.get(field) for field in fields}
                    for _id, record in self._records.items()
                    if _id in ids
                ]

            def field_dump(self):
                return []

            def list_modules(self):
                return set(record["module"] for record in self._records.values())

            def get_xml_records(self, module):
                if module == "other_module":
                    return [
                        """
                        <odoo noupdate="1">
                            <record
                                id="test_noupdate_xmlid"
                                model="upgrade.comparison.config"
                            >
                                <field
                                    name="name"
                                >Noupdate xmlid from other_module</field>
                                <field name="port" eval="7000"/>
                                <field name="username" eval="'admin'"/>
                                <field name="database">some_database</field>
                            </record>
                        </odoo>
                        """
                    ]

        def local_get_xml_records(module):
            if module == "upgrade_analysis":
                return [
                    """
                    <odoo noupdate="1">
                        <record
                            id="test_noupdate_xmlid"
                            model="upgrade.comparison.config"
                        >
                            <field
                                name="name"
                            >Noupdate xmlid from upgrade_analysis</field>
                        </record>
                    </odoo>
                    """
                ]

        written_files = {}

        def write_file(module_name, version, content, filename="upgrade_analysis.txt"):
            written_files[f"{module_name}-{version}-{filename}"] = content

        # Pretend the "database" field is declared in a module that depends on
        # (and is therefore not reachable from) upgrade_analysis.
        database_field = self.env["upgrade.comparison.config"]._fields["database"]

        with (
            patch.object(analysis.config_id.__class__, "get_connection"),
            patch.object(
                analysis.__class__, "_get_remote_model"
            ) as patched_get_remote_model,
            patch.object(analysis.__class__, "_write_file") as patched_write_file,
            patch.object(
                self.env["upgrade.record"].__class__, "get_xml_records"
            ) as patched_get_xml_records,
            patch.object(database_field, "_module", "some_dependent_module"),
        ):
            patched_get_remote_model.side_effect = lambda *args: RemoteUpgradeRecord()
            patched_get_xml_records.side_effect = local_get_xml_records
            patched_write_file.side_effect = write_file
            analysis.analyze()

        expected_noupdate_content = """<?xml version='1.0' encoding='utf-8'?>
<odoo>
  <record id="test_noupdate_xmlid" model="upgrade.comparison.config">
    <field name="name">Noupdate xmlid from upgrade_analysis</field>
    <field name="port" eval="8069"/>
  </record>
</odoo>
"""
        self.assertEqual(
            written_files[
                f"upgrade_analysis-{upgrade_analysis_version}-noupdate_changes.xml"
            ],
            expected_noupdate_content,
        )
