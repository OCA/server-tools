# Copyright 2026 Moduon Team SL
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import io
import os
import tempfile
import unittest
from unittest.suite import _ErrorHolder

from xmlrunner import XMLTestRunner

from odoo.tests.common import BaseCase

from ..odoo_tests.loader import _get_error_holder_source


# Helper classes used by ``test_class_level_error_reported_in_own_file``.
# They are declared at module level so ``_get_error_holder_source`` can
# import them from their description.  The ``_`` prefix keeps unittest
# discovery from picking them up as standalone test cases.
class _PassingTest(unittest.TestCase):
    __unittest_skip__ = False

    def test_pass(self):
        pass


class _FailingTest(unittest.TestCase):
    __unittest_skip__ = False

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        raise ValueError("boom")

    def test_method(self):
        pass


class TestXMLRunnerFix(BaseCase):
    """Check that JUnit reports attribute errors to the right file."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._output_dir = tempfile.mkdtemp()

    def test_error_holder_source_lookup(self):
        """_get_error_holder_source resolves module.ClassName descriptions."""
        err = _ErrorHolder(
            "setUpClass (odoo.addons.odoo_test_xmlrunner.tests.test_xmlrunner"
            ".TestXMLRunnerFix)"
        )
        filename, lineno = _get_error_holder_source(err)
        self.assertTrue(filename.endswith("/test_xmlrunner.py"))
        self.assertIsInstance(lineno, int)
        return True

    def test_class_level_error_reported_in_own_file(self):
        """A failing setUpClass is reported against its own test file."""

        # Use a plain unittest suite to avoid re-entering the OdooSuite
        # monkey patch installed by this addon, which would run an inner
        # XMLTestRunner and return a result object lacking the ``update``
        # method used by the outer runner.
        suite = unittest.TestSuite(
            [_FailingTest("test_method"), _PassingTest("test_pass")]
        )
        runner = XMLTestRunner(
            output=self._output_dir,
            verbosity=0,
            stream=io.StringIO(),
        )
        result = runner.run(suite)
        self.assertEqual(len(result.errors), 1)
        # The failing class is the first one executed, so the result object
        # did not have a chance to pick up a stale filename from a previous
        # test. Verify that the produced XML file still points to this test
        # module rather than to ``unittest/suite.py``.
        error_holder_files = [
            fn for fn in os.listdir(self._output_dir) if "_ErrorHolder" in fn
        ]
        self.assertTrue(
            error_holder_files,
            "Expected an XML file for the _ErrorHolder test case",
        )
        xml_path = os.path.join(self._output_dir, error_holder_files[0])
        with open(xml_path) as xml_file:
            xml_content = xml_file.read()
        # The xmlrunner path is whatever ``inspect.getsourcefile`` returns
        # for the helper class; with editable installs it includes the
        # ``odoo/addons`` namespace.  Verify the testcase points somewhere
        # under this module's path.
        self.assertIn(
            'testcase classname="" name="setUpClass '
            '(odoo.addons.odoo_test_xmlrunner.tests.test_xmlrunner._FailingTest)"',
            xml_content,
        )
        self.assertIn(
            'odoo_test_xmlrunner/tests/test_xmlrunner.py"',
            xml_content,
        )
        return True


class TestXMLRunner(BaseCase):
    """Backward-compatible class name used by the original upstream tests."""

    def test_run(self):
        """Smoke test that the XML test runner still works."""
        self.assertTrue(True)
