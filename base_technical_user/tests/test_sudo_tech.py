# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.tests import TransactionCase


class SudoTechCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(SudoTechCase, cls).setUpClass()
        cls.user_tech = (
            cls.env["res.users"]
            .with_context(tracking_disable=True, no_reset_password=True)
            .create({"login": "tech", "name": "tech"})
        )
        cls.company = cls.env.ref("base.main_company")
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
