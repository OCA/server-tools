# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.exceptions import UserError
from odoo.tests import TransactionCase


class SudoTechCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.ref("base.main_company")
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.company_2 = cls.env["res.company"].create(
            {
                "name": "Company 2 tech",
            }
        )
        cls.company_3 = cls.env["res.company"].create(
            {
                "name": "Company 3 NO tech",
                "user_tech_id": False,
            }
        )
        cls.user_tech = (
            cls.env["res.users"]
            .with_context(no_reset_password=True)
            .create({"login": "tech", "name": "tech"})
        )
        cls.user_tech_2 = (
            cls.env["res.users"]
            .with_context(no_reset_password=True)
            .with_company(cls.company_2)
            .create({"login": "tech2", "name": "tech2", "company_id": cls.company_2.id})
        )
        partner_demo = cls.env["res.partner"].create(
            {
                "name": "Demo User",
                "email": "demo@demo.com",
            }
        )
        cls.user_demo = (
            cls.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "partner_id": partner_demo.id,
                    "login": "demo test",
                    "password": "demo test",
                    "company_id": cls.company.id,
                    "company_ids": [
                        (6, 0, [cls.company.id, cls.company_2.id, cls.company_3.id])
                    ],
                    "group_ids": [
                        (
                            6,
                            0,
                            [
                                cls.env.ref("base.group_user").id,
                                cls.env.ref("base.group_partner_manager").id,
                                cls.env.ref("base.group_allow_export").id,
                            ],
                        )
                    ],
                }
            )
        )

        partner_demo.user_id = cls.user_demo

        cls.env = cls.env(user=cls.user_demo.id)

    def test_sudo_tech(self):
        self.company.user_tech_id = self.user_tech
        self_tech = self.env["res.partner"].sudo_tech()
        self.assertEqual(self_tech.env.uid, self.user_tech.id)

    def test_sudo_tech_missing_return_sudo(self):
        self_tech = self.env["res.partner"].sudo_tech()
        self.assertEqual(self_tech.env.uid, self.user_demo.id)

    def test_sudo_tech_missing_raise(self):
        with self.assertRaises(UserError):
            self.env["res.partner"].sudo_tech(raise_if_missing=True)

    def test_sudo_tech_company_2(self):
        self.company_2.user_tech_id = self.user_tech_2
        self_tech = self.env["res.partner"].with_company(self.company_2).sudo_tech()
        self.assertEqual(self_tech.env.uid, self.user_tech_2.id)

    def test_sudo_tech_company_2_record(self):
        # We switch company twice to fill in allowed_company_ids
        user = self.env.user.with_company(self.company_2).with_company(self.company)
        self.assertEqual(
            self.company,
            user.env.company,
        )
        self.company_2.user_tech_id = self.user_tech_2
        self_tech = user.with_company(self.company_2).sudo_tech()
        self.assertEqual(self_tech.env.uid, self.user_tech_2.id)

    def test_sudo_tech_company_3(self):
        """
        Ensure the error message is related to the
        active company when there is no technical user.
        """
        user = self.env.user.with_company(self.company_3)
        self.assertEqual(self.company_3, user.env.company)
        self.assertNotEqual(user.env.company, user.company_id)
        with self.assertRaises(UserError) as em:
            user.sudo_tech(raise_if_missing=True)
        self.assertIn(self.company_3.name, em.exception.args[0])
        self.assertNotIn(user.company_id.name, em.exception.args[0])
