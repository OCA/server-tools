# Copyright 2022 Camptocamp SA
# @author: Simone Orsi <simone.orsi@camptocamp.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


import unittest

from ..decorator import disable_rpc


@disable_rpc()
class All:
    pass


@disable_rpc("create")
class One:
    pass


@disable_rpc("create", "write")
class Multi:
    pass


class TestDecorator(unittest.TestCase):
    def test_all(self):
        self.assertEqual(All._disable_rpc, ("all",))

    def test_one(self):
        self.assertEqual(One._disable_rpc, ("create",))

    def test_multi(self):
        self.assertEqual(Multi._disable_rpc, ("create", "write"))
