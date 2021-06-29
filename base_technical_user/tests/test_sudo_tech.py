# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.tests import TransactionCase


class SudoTechCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_2 = cls.env["res.company"].create(
            {
                "name": "Company 2 tech",
            }
        )
        cls.user_tech = (
            cls.env["res.users"]
            .with_context(tracking_disable=True, no_reset_password=True)
            .create({"login": "tech", "name": "tech"})
        )
        cls.company = cls.env.ref("base.main_company")
        cls.user_tech_2 = (
            cls.env["res.users"]
            .with_context(tracking_disable=True, no_reset_password=True)
            .with_company(cls.company_2)
            .create({"login": "tech2", "name": "tech2", "company_id": cls.company_2.id})
        )
        cls.env(user=cls.env.ref("base.user_demo").id)

    def test_sudo_tech(self):
        self.company.user_tech_id = self.user_tech
        self_tech = self.env["res.partner"].sudo_tech()
        self.assertEqual(self_tech._uid, self.user_tech.id)

    def test_sudo_tech_missing_return_sudo(self):
        self_tech = self.env["res.partner"].sudo_tech()
        self.assertEqual(self_tech._uid, SUPERUSER_ID)

    def test_sudo_tech_missing_raise(self):
        with self.assertRaises(UserError):
            self.env["res.partner"].sudo_tech(raise_if_missing=True)

    def test_sudo_tech_company_2(self):
        self.company_2.user_tech_id = self.user_tech_2
        self_tech = self.env["res.partner"].with_company(self.company_2).sudo_tech()
        self.assertEqual(self_tech._uid, self.user_tech_2.id)

    def test_sudo_tech_company_2_record(self):
        # We switch company twice to fill in allowed_company_ids
        user = self.env.user.with_company(self.company_2).with_company(self.company)
        self.assertEqual(
            self.company,
            user.env.company,
        )
        self.company_2.user_tech_id = self.user_tech_2
        self_tech = user.with_company(self.company_2).sudo_tech()
        self.assertEqual(self_tech._uid, self.user_tech_2.id)
