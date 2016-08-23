import openerp.tests

from .util.odoo_tests import TestBase
from .util.singleton import Singleton


class TestMemory(object):
    """Keep records in memory across tests."""
    __metaclass__ = Singleton


@openerp.tests.common.at_install(False)
@openerp.tests.common.post_install(True)
class Test(TestBase):

    def setUp(self):
        super(Test, self).setUp()
        self.memory = TestMemory()

    # TODO Tests.
