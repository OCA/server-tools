# Copyright 2018 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp.tests.common import TransactionCase


class TestProfiling(TransactionCase):

    def test_profile_creation(self):
        """We are testing the creation of a profile."""
        prof_obj = self.env['profiler.profile']
        profile = prof_obj.create({'name': 'this_profiler'})
        profile.enable()
        profile.disable()
