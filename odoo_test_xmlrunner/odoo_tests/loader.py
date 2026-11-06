import os
from unittest.mock import patch

from xmlrunner import XMLTestRunner

from odoo.tests.common import OdooSuite
from odoo.tools import config

if config["test_enable"]:
    unpatched_run = OdooSuite.run

    def run(self, result):
        # Override : Get and create a config dir
        test_result_directory = config.get("test_result_directory", "test_results")
        # create test result directory if not exists
        if not os.path.exists(test_result_directory):
            os.makedirs(test_result_directory)

        # Suite run method will be called by the XMLTestRunner,
        # so we need to run the original run method
        with patch.object(self, "run", lambda result: unpatched_run(self, result)):
            # Override : XMLTestRunner to run the tests and generate XML reports
            results = XMLTestRunner(
                output=test_result_directory,
                verbosity=2,
            ).run(self)

        result.update(results)
        return result

    patch("odoo.tests.common.OdooSuite.run", run).start()
