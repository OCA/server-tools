# Copyright (C) 2026 XXP
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase

MODULE_MODEL = "ir.module.module"
DEP_MODEL = "ir.module.module.dependency"


class TestQuickUpgrade(TransactionCase):
    """Tests for the "Quick upgrade" action.

    The disk-backed helpers ``update_list`` and ``get_module_info`` are
    stubbed so the tests run against controlled in-database fixtures and do
    not depend on what is actually present on the addons path.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Module = cls.env[MODULE_MODEL]
        cls.Dependency = cls.env[DEP_MODEL]

        # Target module and an installed module that depends on it.
        cls.module_a = cls.Module.create({"name": "test_qu_a", "state": "installed"})
        cls.module_b = cls.Module.create({"name": "test_qu_b", "state": "installed"})
        # test_qu_b depends on test_qu_a (reverse dependency of A).
        cls.Dependency.create({"name": "test_qu_a", "module_id": cls.module_b.id})

        # An uninstalled upstream dependency of the target module.
        cls.module_c = cls.Module.create({"name": "test_qu_c", "state": "uninstalled"})
        cls.Dependency.create({"name": "test_qu_c", "module_id": cls.module_a.id})

    def setUp(self):
        super().setUp()
        model_cls = type(self.Module)
        patch_update = patch.object(model_cls, "update_list", lambda self: None)
        patch_info = patch.object(
            model_cls,
            "get_module_info",
            classmethod(lambda cls, name: {"installable": True}),
        )
        patch_update.start()
        patch_info.start()
        self.addCleanup(patch_update.stop)
        self.addCleanup(patch_info.stop)

    def test_quick_upgrade_does_not_cascade_to_dependents(self):
        """Quick upgrade marks only the selected module, not its dependents."""
        self.module_a.button_quick_upgrade()

        self.assertEqual(self.module_a.state, "to upgrade")
        self.assertEqual(
            self.module_b.state,
            "installed",
            "Quick upgrade must not queue installed modules that depend "
            "on the selected one.",
        )

    def test_standard_upgrade_cascades_to_dependents(self):
        """Control: the standard upgrade still cascades to dependents."""
        self.module_a.button_upgrade()

        self.assertEqual(self.module_a.state, "to upgrade")
        self.assertEqual(
            self.module_b.state,
            "to upgrade",
            "Standard upgrade is expected to keep cascading to dependents.",
        )

    def test_quick_upgrade_installs_missing_upstream_dependency(self):
        """A missing upstream dependency is still installed."""
        self.module_a.button_quick_upgrade()

        self.assertEqual(self.module_a.state, "to upgrade")
        self.assertEqual(
            self.module_c.state,
            "to install",
            "A missing upstream dependency must be queued for install.",
        )

    def test_quick_upgrade_requires_installed_module(self):
        """Quick-upgrading a non-installed module raises the "not installed" error."""
        module_d = self.Module.create({"name": "test_qu_d", "state": "uninstalled"})
        with self.assertRaisesRegex(
            UserError,
            r"Can not upgrade module 'test_qu_d'\. It is not installed\.",
            msg=(
                "Quick upgrade of the uninstalled module test_qu_d must fail on "
                "the state check with the 'not installed' message."
            ),
        ):
            module_d.button_quick_upgrade()

        self.assertEqual(
            module_d.state,
            "uninstalled",
            "A rejected quick upgrade must leave the module state untouched.",
        )

    def test_quick_upgrade_rejects_unknown_dependency(self):
        """A dependency missing from the system raises the "not available" error."""
        module_e = self.Module.create({"name": "test_qu_e", "state": "installed"})
        self.Dependency.create({"name": "test_qu_missing", "module_id": module_e.id})

        with self.assertRaisesRegex(
            UserError,
            r"depends on the module: test_qu_missing",
            msg=(
                "Quick upgrade of test_qu_e must fail on the dependency check "
                "naming the unavailable module test_qu_missing, not on any "
                "other UserError raised earlier in the flow."
            ),
        ):
            module_e.button_quick_upgrade()

    def test_quick_upgrade_empty_recordset_is_noop(self):
        """Calling the action on an empty recordset returns without error."""
        self.assertFalse(
            self.Module.browse().button_quick_upgrade(),
            "Quick upgrade on an empty recordset must return a falsy value "
            "instead of an action or an error.",
        )
