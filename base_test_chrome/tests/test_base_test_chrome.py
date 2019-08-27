# -*- coding: utf-8 -*-
# Copyright 2019 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import unittest
from ..common import HttpCase


class TestBaseTestChrome(HttpCase):

    @unittest.skip(
        'Memory leak in test lead to phantomjs crash, making it unreliable')
    def test_base_test_chrome_web(self):
        self.browser_js('/web/tests?mod=web', '', '', login='admin')
