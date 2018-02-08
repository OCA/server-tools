# -*- coding: utf-8 -*-
# Copyright 2016 Grupo ESOC Ingeniería de Servicios, S.L.U. - Jairo Llopis
# Copyright 2016 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from os import path
from openerp.tests.common import at_install, post_install, TransactionCase


PATH = path.join(path.dirname(__file__), "import_data", "%s.csv")
OPTIONS = {
    "headers": True,
    "quoting": '"',
    "separator": ",",
}


@at_install(False)
@post_install(True)
class ImportCase(TransactionCase):
    def _base_import_record(self, res_model, file_name):
        """Create and return a ``base_import.import`` record."""
        with open(PATH % file_name) as demo_file:
            return self.env["base_import.import"].create({
                "res_model": res_model,
                "file": demo_file.read(),
                "file_name": "%s.csv" % file_name,
                "file_type": "csv",
            })

    def test_res_partner_vat(self):
        """Change name based on VAT."""
        agrolait = self.env.ref("base.res_partner_2")
        agrolait.vat = "BE0477472701"
        record = self._base_import_record("res.partner", "res_partner_vat")
        record.do(["name", "vat", "is_company"], OPTIONS)
        agrolait.env.invalidate_all()
        self.assertEqual(agrolait.name, "Agrolait Changed")

    def test_res_partner_parent_name_is_company(self):
        """Change email based on parent_id, name and is_company."""
        record = self._base_import_record(
            "res.partner", "res_partner_parent_name_is_company")
        record.do(["name", "is_company", "parent_id/id", "email"], OPTIONS)
        self.assertEqual(
            self.env.ref("base.res_partner_address_4").email,
            "changed@agrolait.example.com")

    def test_res_partner_email(self):
        """Change name based on email."""
        record = self._base_import_record("res.partner", "res_partner_email")
        record.do(["email", "name"], OPTIONS)
        self.assertEqual(
            self.env.ref("base.res_partner_address_4").name,
            "Michel Fletcher Changed")

    def test_res_partner_name(self):
        """Change function based on name."""
        record = self._base_import_record("res.partner", "res_partner_name")
        record.do(["function", "name"], OPTIONS)
        self.assertEqual(
            self.env.ref("base.res_partner_address_4").function,
            "Function Changed")

    def test_res_users_login(self):
        """Change name based on login."""
        record = self._base_import_record("res.users", "res_users_login")
        record.do(["login", "name"], OPTIONS)
        self.assertEqual(
            self.env.ref("base.user_demo").name,
            "Demo User Changed")
