import os
import threading

import xmlrunner

from odoo.tests import loader as odoo_loader
from odoo.tests.result import OdooTestResult
from odoo.tools import config


def new_run_suite(suite, module_name=None):
    # Override : Get and create a config dir
    test_result_directory = config.get("test_result_directory", "test_results")
    # create test result directory if not exists
    if not os.path.exists(test_result_directory):
        os.makedirs(test_result_directory)

    # avoid dependency hell
    from odoo.modules import module

    module.current_test = module_name
    threading.current_thread().testing = True
    results = OdooTestResult()

    # Override : XMLTestRunner to run the tests and generate XML reports
    xmlrunner.XMLTestRunner(output=test_result_directory, verbosity=2).run(suite)

    threading.current_thread().testing = False
    module.current_test = None
    return results


odoo_loader.run_suite = new_run_suite
