
from odoo.tests.common import TransactionCase

class TestVapiIntegration(TransactionCase):
    def test_module_install(self):
        # The module should be installed without errors
        self.assertTrue(True)
