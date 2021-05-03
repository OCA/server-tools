# Copyright 2021 Open Source Integrators
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import TransactionCase


class TestUserRoleCompany(TransactionCase):
    def setUp(self):
        super().setUp()
        # COMPANIES
        self.Company = self.env["res.company"]
        self.company1 = self.env.ref("base.main_company")
        self.company2 = self.Company.create({"name": "company2"})
        # ROLES
        self.Role = self.env["res.users.role"]
        self.roleA = self.Role.create({"name": "ROLE All Companies"})
        self.roleB = self.Role.create({"name": "ROLE Company 1"})
        self.roleC = self.Role.create({"name": "ROLE Company 1 and 2"})
        # USER
        # ==Role=== ==Company== C1  C2  C1+C2
        # Role A                Yes Yes Yes
        # Role B    Company1    Yes
        # Role C    Company1    Yes     Yes
        # Role C    Company2        Yes Yes
        self.User = self.env["res.users"]
        user_vals = {
            "name": "ROLES TEST USER",
            "login": "test_user",
            "company_ids": [(6, 0, [self.company1.id, self.company2.id])],
            "role_line_ids": [
                (0, 0, {"role_id": self.roleA.id}),
                (0, 0, {"role_id": self.roleB.id, "company_id": self.company1.id}),
                (0, 0, {"role_id": self.roleC.id, "company_id": self.company1.id}),
                (0, 0, {"role_id": self.roleC.id, "company_id": self.company2.id}),
            ],
        }
        self.test_user = self.User.create(user_vals)
        self.User = self.User.with_user(self.test_user)

    def test_110_company_1(self):
        "Company 1 selected: Tech and Settings roles are activated"
        self.User._set_session_active_roles([self.company1.id])
        active_roles = self.test_user.role_line_ids.filtered("active_role").mapped(
            "role_id"
        )
        self.assertEqual(active_roles, self.roleA | self.roleB | self.roleC)

    def test_120_company_2(self):
        "Company 2 selected: only Tech role enabled"
        self.User._set_session_active_roles([self.company2.id])
        active_roles = self.test_user.role_line_ids.filtered("active_role").mapped(
            "role_id"
        )
        self.assertEqual(active_roles, self.roleA | self.roleC)

    def test_130_company_1_2(self):
        "Settings Role enabled for Company 1 and 2"
        self.User._set_session_active_roles([self.company1.id, self.company2.id])
        active_roles = self.test_user.role_line_ids.filtered("active_role").mapped(
            "role_id"
        )
        self.assertEqual(active_roles, self.roleA | self.roleC)
