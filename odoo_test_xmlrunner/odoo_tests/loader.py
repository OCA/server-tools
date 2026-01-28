import os

from odoo.tools import config

if config["test_enable"]:
    from xmlrunner import XMLTestRunner
    from xmlrunner.result import _XMLTestResult

    from odoo.tests.result import OdooTestResult
    from odoo.tests.suite import OdooSuite

    unpatched_run = OdooSuite.run

    def run(self, result):
        # Override : Get and create a config dir
        test_result_directory = config.get("test_result_directory", "test_results")
        # create test result directory if not exists
        if not os.path.exists(test_result_directory):
            os.makedirs(test_result_directory)

        # Suite run method will be called by the XMLTestRunner,
        # so we need to run the original run method
        unpatched_sub_run = self.run
        self.run = lambda result, debug=False: unpatched_run(self, result, debug)
        # Override : XMLTestRunner to run the tests and generate XML reports
        try:
            results = XMLTestRunner(
                output=test_result_directory,
                verbosity=2,
            ).run(self)
        finally:
            self.run = unpatched_sub_run

        result.update(results)
        return result

    OdooSuite.run = run

    unpatched_update = OdooTestResult.update

    def update(self, other):
        # Adapt _XMLTestResult to OdooTestResult
        if isinstance(other, _XMLTestResult):
            self.failures_count += len(other.failures)
            self.errors_count += len(other.errors)
            self.skipped += len(other.skipped)
            self.testsRun += other.testsRun
        else:
            unpatched_update(self, other)

    OdooTestResult.update = update
