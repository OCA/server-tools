# Copyright (C) 2019-Today: GRAP (<http://www.grap.coop/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import os
from unittest.mock import patch

from odoo.tests import SavepointCase, tagged


@tagged("post_install", "-at_install")
class TestModule(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.IrModuleModule = cls.env["ir.module.module"]
        cls.module = cls.env.ref("base.module_module_analysis")
        # Do not exclude 'tests' because our test module is in it
        set_param = cls.env["ir.config_parameter"].set_param
        set_param("module_analysis.exclude_directories", "demo,readme,lib")

    def test_module_analysis(self):
        # Analyze our fake "test_module"
        with patch(
            "odoo.addons.module_analysis.models.ir_module_module.get_module_path"
        ) as mock_get_module_path:
            mock_get_module_path.return_value = os.path.join(
                os.path.dirname(__file__), "module"
            )
            self.module._analyse_code()
            mock_get_module_path.assert_called_once()
            self.assertEqual(self.module.python_code_qty, 13)
            self.assertEqual(self.module.xml_code_qty, 24)
            self.assertEqual(self.module.css_code_qty, 6)
            self.assertEqual(self.module.js_code_qty, 7)
