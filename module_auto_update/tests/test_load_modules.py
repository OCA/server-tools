# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from unittest.mock import patch

from odoo import release
from odoo.tests import TransactionCase, tagged
from odoo.tools import config

from ..patches.load_modules import get_updateable_modules


@tagged("post_install", "-at_install")
class TestLoadModules(TransactionCase):
    def setUp(self):
        super().setUp()
        self.module = self.env["ir.module.module"].search(
            [("name", "=", "web")], limit=1
        )
        self.assertEqual(self.module.state, "installed")

    @patch.dict(config.options, {"init": []})
    def test_get_updateable_modules(self):
        # FIXME AttributeError: 'ir.module.module' object has no attribute '_save_installed_checksums' # noqa: E501
        self.skipTest("FIXME breaks test_module")
        self.assertEqual(self.module.latest_version, self.module.installed_version)
        self.assertNotIn(
            "web", get_updateable_modules(self.registry), "should ignore same version"
        )

    @patch.dict(config.options, {"init": []})
    def test_get_updateable_modules_downgrade(self):
        # FIXME AttributeError: 'ir.module.module' object has no attribute '_save_installed_checksums'# noqa: E501
        self.skipTest("FIXME breaks test_module")
        self.module.latest_version = f"{release.serie}.999999.0"
        self.assertNotIn(
            "web", get_updateable_modules(self.registry), "should ignore downgrade"
        )

    @patch.dict(config.options, {"init": ["web"]})
    def test_get_updateable_modules_init(self):
        self.assertFalse(get_updateable_modules(self.registry), "should ignore install")

    @patch.dict(config.options, {"init": []})
    def test_get_updateable_modules_upgrade(self):
        self.skipTest(
            "TODO fails with AssertionError: 'web' not found in [] : should upgrade"
        )
        self.module.latest_version = f"{release.serie}.0.0"
        self.assertIn("web", get_updateable_modules(self.registry), "should upgrade")
