import inspect
import os
import re

from odoo.tools import config

if config["test_enable"]:
    from unittest.suite import _ErrorHolder

    from xmlrunner import XMLTestRunner
    from xmlrunner.result import _XMLTestResult, failfast

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

    _ERROR_HOLDER_PATTERN = re.compile(
        r"\((?P<module>[a-zA-Z_][a-zA-Z0-9_.]*)\."
        r"(?P<classname>[a-zA-Z_][a-zA-Z0-9_]*)\)"
    )

    def _get_error_holder_source(test):
        """Return the source file and line for an unittest ``_ErrorHolder``.

        ``_ErrorHolder`` instances are created by :class:`unittest.suite.TestSuite`
        when a class-level ``setUpClass`` or ``tearDownClass`` fails. They carry a
        description such as ``setUpClass (module.ClassName)`` but have no reference
        to the actual class, so :class:`xmlrunner.result._XMLTestResult` cannot
        determine their source location and falls back to the previously recorded
        file (often belonging to a completely different test). This helper parses the
        description and uses :mod:`inspect` to locate the real class.
        """
        match = _ERROR_HOLDER_PATTERN.search(str(test))
        if not match:
            return None, None
        try:
            module = __import__(
                match.group("module"), fromlist=[match.group("classname")]
            )
            test_class = getattr(module, match.group("classname"))
            filename = inspect.getsourcefile(test_class)
            _, lineno = inspect.getsourcelines(test_class)
            return filename, lineno
        except Exception:
            return None, None

    unpatched_xml_start_test = _XMLTestResult.startTest

    def xml_start_test(self, test):
        unpatched_xml_start_test(self, test)
        if isinstance(test, _ErrorHolder) or test.__class__.__name__ == "_ErrorHolder":
            filename, lineno = _get_error_holder_source(test)
            if filename is not None:
                self.filename = filename
                self.lineno = lineno

    _XMLTestResult.startTest = xml_start_test

    unpatched_xml_add_error = _XMLTestResult.addError

    @failfast
    def xml_add_error(self, test, err):
        # ``_XMLTestResult.startTest`` is never called for ``_ErrorHolder``
        # instances created when ``setUpClass``/``tearDownClass`` fails, so
        # ``self.filename`` retains the value from a previous test and the
        # produced ``_TestInfo`` ends up with the wrong source file. Compute
        # the real source file from the error holder description before
        # delegating to the original implementation, then patch the recorded
        # test info.
        filename = lineno = None
        if getattr(test, "__class__", None).__name__ == "_ErrorHolder":
            filename, lineno = _get_error_holder_source(test)
        unpatched_xml_add_error(self, test, err)
        if filename is not None:
            self.errors[-1][0].filename = filename
            self.errors[-1][0].lineno = lineno

    _XMLTestResult.addError = xml_add_error

    unpatched_xml_add_failure = _XMLTestResult.addFailure

    @failfast
    def xml_add_failure(self, test, err):
        # Same fix as ``addError`` for class-level failures.
        filename = lineno = None
        if getattr(test, "__class__", None).__name__ == "_ErrorHolder":
            filename, lineno = _get_error_holder_source(test)
        unpatched_xml_add_failure(self, test, err)
        if filename is not None:
            self.failures[-1][0].filename = filename
            self.failures[-1][0].lineno = lineno

    _XMLTestResult.addFailure = xml_add_failure
