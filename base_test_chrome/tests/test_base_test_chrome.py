# -*- coding: utf-8 -*-
# Copyright 2019 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from ..common import HttpCase


class TestBaseTestChrome(HttpCase):
    def test_base_test_chrome_basic(self):
        self.browser_js('/web', 'console.log("ok")')

    def test_base_test_chrome_web(self):
        self.browser_js('/web/tests?mod=web', '', '', login='admin')
