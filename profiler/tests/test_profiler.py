# coding: utf-8
# License AGPL-3 or later (http://www.gnu.org/licenses/lgpl).
# Copyright 2016 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>

import unittest

from openerp import tests


@tests.at_install(False)
@tests.post_install(True)
class TestProfiler(tests.HttpCase):

    @unittest.skip("phantomjs tests async for 8.0 are so flaky")
    def test_profiler_tour(self):
        self.phantom_js('/web', "openerp.Tour.run('profile_run', 'test')",
                        'openerp.Tour.tours.profile_run', login='admin')
