import os
import threading
import time
import unittest
import logging
import xmlrunner

from odoo.service import server as odoo_server
from odoo.modules.module import unwrap_suite
from odoo.modules.module import get_test_modules
import odoo
import odoo.tools as tools


_logger = logging.getLogger(__name__)


def new_run_unit_tests(module_name, dbname, position='at_install'):
    """
    :returns: ``True`` if all of ``module_name``'s tests succeeded, ``False``
              if any of them failed.
    :rtype: bool
    """
    # Override : Get and create a config dir
    test_result_directory = tools.config.get(
        "test_result_directory", "test_results"
    )
    # create test result directory if not exists
    if not os.path.exists(test_result_directory):
        os.makedirs(test_result_directory)

    global current_test
    # avoid dependency hell
    from odoo.tests.common import TagsSelector, OdooSuite
    current_test = module_name
    mods = get_test_modules(module_name)
    threading.currentThread().testing = True
    config_tags = TagsSelector(tools.config['test_tags'])
    position_tag = TagsSelector(position)
    r = True
    for m in mods:
        tests = unwrap_suite(unittest.TestLoader().loadTestsFromModule(m))
        suite = OdooSuite(
            t for t in tests if position_tag.check(t) and config_tags.check(t)
        )

        if suite.countTestCases():
            t0 = time.time()
            t0_sql = odoo.sql_db.sql_counter
            _logger.info('%s running tests.', m.__name__)

            # Override : XMLTestRunner to run the tests and generate XML reports
            result = xmlrunner.XMLTestRunner(
                output=test_result_directory, verbosity=2
            ).run(suite)

            if time.time() - t0 > 5:
                _logger.log(
                    25, "%s tested in %.2fs, %s queries",
                    m.__name__, time.time() - t0,
                    odoo.sql_db.sql_counter - t0_sql
                    )
            if not result.wasSuccessful():
                r = False
                _logger.error(
                    "Module %s: %d failures, %d errors",
                    module_name, len(result.failures), len(result.errors)
                )

    current_test = None
    threading.currentThread().testing = False
    return r


odoo_server.run_unit_tests = new_run_unit_tests
