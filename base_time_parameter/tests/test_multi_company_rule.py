# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import date

from odoo.modules.migration import load_script
from odoo.tests import new_test_user
from odoo.tests.common import TransactionCase
from odoo.tools.misc import file_path

RULES = (
    "base_time_parameter.base_time_parameter_multi_company_rule",
    "base_time_parameter.base_time_parameter_version_multi_company_rule",
)
OLD_DOMAIN = "[('company_id', 'in', company_ids)]"
NEW_DOMAIN = "['|', ('company_id', '=', False), ('company_id', 'in', company_ids)]"


class TestMultiCompanyRule(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.other_company = cls.env["res.company"].create({"name": "Other Company"})
        cls.user = new_test_user(
            cls.env,
            login="time_parameter_user",
            groups="base.group_user,base_time_parameter.group_time_parameter",
            company_id=cls.company.id,
            company_ids=[(6, 0, cls.company.ids)],
        )
        cls.other_user = new_test_user(
            cls.env,
            login="time_parameter_other_user",
            groups="base.group_user,base_time_parameter.group_time_parameter",
            company_id=cls.other_company.id,
            company_ids=[(6, 0, cls.other_company.ids)],
        )

    def _create_parameter(self, value, company=False):
        return self.env["base.time.parameter"].create(
            {
                "code": "TEST_RULE",
                "type": "string",
                "company_id": company and company.id,
                "version_ids": [
                    (0, 0, {"date_from": date(2022, 1, 1), "value": value})
                ],
            }
        )

    def test_user_reads_global_parameter(self):
        parameter = self._create_parameter("GLOBAL")
        Parameter = self.env["base.time.parameter"].with_user(self.user)
        self.assertEqual(
            Parameter.search([("code", "=", "TEST_RULE")]),
            parameter,
            "A parameter with no company is visible to the users of any company",
        )
        self.assertEqual(
            parameter.with_user(self.user).version_ids.value,
            "GLOBAL",
            "... and so are its versions",
        )
        value = (
            self.env["res.partner"].with_user(self.user).get_time_parameter("TEST_RULE")
        )
        self.assertEqual(value, "GLOBAL")

    def test_user_gets_company_parameter_over_global_one(self):
        self._create_parameter("GLOBAL")
        self._create_parameter("COMPANY", company=self.company)
        value = (
            self.env["res.partner"].with_user(self.user).get_time_parameter("TEST_RULE")
        )
        self.assertEqual(value, "COMPANY", "The user gets the value of the company")
        # The parameter of a company stays private to it: the user of another
        # company only sees the global one.
        Parameter = self.env["base.time.parameter"].with_user(self.other_user)
        self.assertEqual(
            Parameter.search([("code", "=", "TEST_RULE")]).mapped("company_id"),
            self.env["res.company"],
        )
        value = (
            self.env["res.partner"]
            .with_user(self.other_user)
            .get_time_parameter("TEST_RULE")
        )
        self.assertEqual(value, "GLOBAL", "Another company keeps the global value")

    def _migrate(self):
        script = load_script(
            file_path("base_time_parameter/migrations/18.0.1.0.2/post-migration.py"),
            "base_time_parameter_post_migration",
        )
        script.migrate(self.env.cr, "18.0.1.0.1")
        self.env.invalidate_all()

    def test_migration_rewrites_shipped_domain(self):
        rules = self.env["ir.rule"].browse([self.env.ref(x).id for x in RULES])
        # As stored by the previous version, layout of the data file included.
        rules[0].domain_force = OLD_DOMAIN
        rules[1].domain_force = f"\n            {OLD_DOMAIN}\n        "
        self._migrate()
        for rule in rules:
            self.assertEqual(rule.domain_force, NEW_DOMAIN)
        # Running it again changes nothing.
        self._migrate()
        for rule in rules:
            self.assertEqual(rule.domain_force, NEW_DOMAIN)

    def test_migration_keeps_customized_domain(self):
        custom = "[('company_id', '=', company_id)]"
        rule = self.env.ref(RULES[0])
        rule.domain_force = custom
        self._migrate()
        self.assertEqual(rule.domain_force, custom, "An edited rule is left alone")
