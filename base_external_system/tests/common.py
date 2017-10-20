# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from contextlib import contextmanager
from mock import MagicMock

from odoo.tests.common import TransactionCase


class Common(TransactionCase):

    @contextmanager
    def _mock_method(self, method_name, method_obj=None):
        if method_obj is None:
            method_obj = self.record
        magic = MagicMock()
        method_obj._patch_method(method_name, magic)
        try:
            yield magic
        finally:
            method_obj._revert_method(method_name)
