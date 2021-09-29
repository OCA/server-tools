# Copyright 2021 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestSearchMulti(SavepointCase):
    """Tests for search on name_search (account.account)

    The name search on account.account is quite complex, make sure
    we have all the correct results
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ResUser = cls.env["res.users"]
        cls.demo = cls.env.ref("base.user_demo")
        cls.admin = cls.env.ref("base.user_admin")

    def test_name_search(self):
        # Search 1 value
        self.all_name = self.demo.name
        users = self.ResUser.search(args=[("name", "ilike", self.all_name)])
        self.assertEqual(len(users), 1)

        # Search multi value
        self.all_name = "".join(["{", self.demo.name, " ", self.admin.name, "}"])
        users = self.ResUser.search(args=[("name", "ilike", self.all_name)])
        self.assertEqual(len(users), 2)
