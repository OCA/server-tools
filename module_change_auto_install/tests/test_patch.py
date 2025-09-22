import logging
import os
import tempfile
from unittest.mock import patch

from odoo.modules.module import Manifest
from odoo.tests.common import TransactionCase
from odoo.tools import config

import odoo.addons.module_change_auto_install as mcai

_logger = logging.getLogger(__name__)


def make_manifest(name, depends=None, auto_install=False):
    tmpdir = tempfile.mkdtemp()
    module_path = os.path.join(tmpdir, name)
    os.makedirs(module_path, exist_ok=True)

    manifest_content = {
        "name": name,
        "author": "Author",
        "license": "AGPL-3",
        "depends": depends or [],
        "auto_install": auto_install,
    }
    return Manifest(path=module_path, manifest_content=manifest_content)


class TestModuleChangeAutoInstall(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Apply patch once for all tests
        mcai.post_load()

    def test_default_auto_install(self):
        m = make_manifest("test_module", ["base"], auto_install=False)
        self.assertFalse(m._Manifest__manifest_cached["auto_install"])

    @patch.dict(
        config.options,
        {
            "module_change_auto_install.modules_disabled": "test_module",
        },
    )
    def test_disabled_module(self):
        m = make_manifest("test_module", ["base"], auto_install=True)
        self.assertTrue(m._Manifest__manifest_cached["auto_install"] is False)

    @patch.dict(
        config.options, {"module_change_auto_install.modules_enabled": "test_module"}
    )
    def test_enabled_module_unconditional(self):
        m = make_manifest("test_module", ["base"], auto_install=False)
        # Should return its dependencies as auto-install condition
        self.assertEqual(m._Manifest__manifest_cached["auto_install"], set(["base"]))

    @patch.dict(
        config.options,
        {
            "module_change_auto_install.modules_enabled": "test_module:dep1/dep2",
        },
    )
    def test_enabled_module_with_specific_dependencies(self):
        m = make_manifest("test_module", ["base"], auto_install=False)
        self.assertEqual(
            m._Manifest__manifest_cached["auto_install"], set(["dep1", "dep2"])
        )

    @patch.dict(
        config.options, {"module_change_auto_install.modules_enabled": "test_module:"}
    )
    def test_enabled_module_all_cases(self):
        m = make_manifest("test_module", ["base"], auto_install=False)
        self.assertEqual(m._Manifest__manifest_cached["auto_install"], set())
