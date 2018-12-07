# coding: utf-8
# @ 2016 Florian da Costa @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import openerp.tests.common as common
from openerp import api
from io import StringIO


# TODO: Migration to 11.0
class ContextualStringIO(StringIO):
    """
    snippet from http://bit.ly/1HfH6uW (stackoverflow)
    """

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
        return False


class TestConnection(common.TransactionCase):

    def setUp(self):
        super(TestConnection, self).setUp()
        self.registry.enter_test_mode()
        self.env = api.Environment(self.registry.test_cr, self.env.uid,
                                   self.env.context)

    def tearDown(self):
        self.registry.leave_test_mode()
        super(TestConnection, self).tearDown()
