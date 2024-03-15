# Copyright 2021 Akretion (http://www.akretion.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import AccessError
from odoo.tests import SavepointCase


class TestPartnerRestrict(SavepointCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env.ref("base.res_partner_3")
        self.user = self.env.ref("base.user_demo")

    def test_partner_edition_restricted(self):
        self.partner.name = "This should work"
        self.partner.restrict_edition_to_superuser = True
        with self.assertRaises(AccessError):
            self.partner.with_user(self.user.id).name = "This should raise"
