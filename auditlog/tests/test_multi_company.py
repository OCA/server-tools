import json

from odoo.tests.common import Form, TransactionCase, new_test_user


class TestAuditlogMultiCompany(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_model = cls.env.ref("base.model_res_partner")
        cls.res_company = cls.env["res.company"]
        cls.auditlog_log = cls.env["auditlog.log"]
        cls.auditlog_rule = cls.env["auditlog.rule"]
        cls.res_partner = cls.env["res.partner"]
        cls.ir_rule = cls.env["ir.rule"]
        cls.res_partner_category = cls.env["res.partner.category"]
        cls.res_partner_category_model = cls.env["ir.model"]._get(
            cls.res_partner_category._name
        )
        cls.partner_rule = cls.auditlog_rule.create(
            {
                "name": "Test rule for multi-company",
                "model_id": cls.partner_model.id,
                "log_read": False,
                "log_create": False,
                "log_write": True,
                "log_unlink": False,
                "log_type": "full",
                "state": "subscribed",
            }
        )
        cls.partner = cls.res_partner.create({"name": "Test Partner"})
        cls.main_company = cls.env.ref("base.main_company")
        cls.main_company_user = new_test_user(
            cls.env,
            login="main.company.user",
            groups="base.group_user,base.group_partner_manager",
            company_id=cls.main_company.id,
            company_ids=cls.main_company.ids,
        )
        cls.other_company = cls.res_company.create({"name": "Other Company"})
        cls.other_company_user = new_test_user(
            cls.env,
            login="other.company.user",
            groups="base.group_user,base.group_partner_manager",
            company_id=cls.other_company.id,
            company_ids=cls.other_company.ids,
        )
        cls.category_1 = cls.res_partner_category.create({"name": "Category 1"})
        cls.category_2 = cls.res_partner_category.create({"name": "Category 2"})
        cls.category_3 = cls.res_partner_category.create({"name": "Category 3"})
        cls.category_4 = cls.res_partner_category.create({"name": "Category 4"})
        cls.env["ir.model.fields"].sudo().create(
            [
                {
                    "name": "x_company_id",
                    "field_description": "Company",
                    "model_id": cls.res_partner_category_model.id,
                    "ttype": "many2one",
                    "relation": cls.res_company._name,
                }
            ]
        )
        cls.partner_domain = [
            ("model_id", "=", cls.partner_model.id),
            ("method", "=", "write"),
            ("res_id", "=", cls.partner.id),
        ]

    @classmethod
    def tearDownClass(cls):
        cls.partner_rule.unlink()
        super().tearDownClass()

    def _setup_multi_company(self):
        self.ir_rule.create(
            {
                "name": "Multi-Company Rule",
                "model_id": self.res_partner_category_model.id,
                "domain_force": "['|', ('x_company_id', '=', False),"
                " ('x_company_id', 'in', company_ids)]",
            }
        )
        self.category_1.x_company_id = self.main_company
        self.category_2.x_company_id = self.other_company
        self.category_3.x_company_id = self.main_company
        self.category_4.x_company_id = self.other_company

    def _set_category_with_form(self, user, category):
        with Form(self.partner.with_user(user)) as f:
            f.category_id.add(category)

    def _get_old_value(self):
        return json.loads(
            self.auditlog_log.search(self.partner_domain, order="id desc")[
                0
            ].line_ids.old_value
        )

    def _get_new_value(self):
        return json.loads(
            self.auditlog_log.search(self.partner_domain, order="id desc")[
                0
            ].line_ids.new_value
        )

    def test_10_01_multi_company_not_restricted(self):
        self._set_category_with_form(self.main_company_user, self.category_1)
        self.assertFalse(self._get_old_value())
        self.assertEqual(self._get_new_value(), self.category_1.ids)

        self._set_category_with_form(self.other_company_user, self.category_2)
        self.assertEqual(self._get_old_value(), self.category_1.ids)
        self.assertEqual(self._get_new_value(), (self.category_1 | self.category_2).ids)
        with Form(self.partner.with_user(self.main_company_user)) as f:
            self.assertEqual(
                f.category_id._get_ids(), (self.category_1 | self.category_2).ids
            )
        with Form(self.partner.with_user(self.other_company_user)) as f:
            self.assertEqual(
                f.category_id._get_ids(), (self.category_1 | self.category_2).ids
            )

    def test_10_02_multi_company_not_restricted(self):
        self.partner.with_user(self.main_company_user).category_id |= self.category_1
        self.assertFalse(self._get_old_value())
        self.assertEqual(self._get_new_value(), self.category_1.ids)

        self.partner.with_user(self.other_company_user).category_id |= self.category_2
        self.assertEqual(self._get_old_value(), self.category_1.ids)
        self.assertEqual(self._get_new_value(), (self.category_1 | self.category_2).ids)
        self.assertEqual(
            self.partner.with_user(self.main_company_user).category_id,
            (self.category_1 | self.category_2),
        )
        self.assertEqual(
            self.partner.with_user(self.other_company_user).category_id,
            (self.category_1 | self.category_2),
        )

    def test_20_01_multi_company_restricted(self):
        self._setup_multi_company()

        self._set_category_with_form(self.main_company_user, self.category_1)
        self.assertFalse(self._get_old_value())
        self.assertEqual(self._get_new_value(), self.category_1.ids)
        self._set_category_with_form(self.main_company_user, self.category_3)
        self.assertEqual(self._get_old_value(), self.category_1.ids)
        self.assertEqual(self._get_new_value(), (self.category_1 | self.category_3).ids)

        self._set_category_with_form(self.other_company_user, self.category_2)
        self.assertFalse(self._get_old_value())
        self.assertEqual(self._get_new_value(), self.category_2.ids)
        self._set_category_with_form(self.other_company_user, self.category_4)
        self.assertEqual(self._get_old_value(), self.category_2.ids)
        self.assertEqual(self._get_new_value(), (self.category_2 | self.category_4).ids)

        with Form(self.partner.with_user(self.main_company_user)) as f:
            self.assertEqual(
                f.category_id._get_ids(), (self.category_1 | self.category_3).ids
            )
        with Form(self.partner.with_user(self.other_company_user)) as f:
            self.assertEqual(
                f.category_id._get_ids(), (self.category_2 | self.category_4).ids
            )

    def test_20_02_multi_company_restricted(self):
        self._setup_multi_company()

        self.partner.with_user(self.main_company_user).category_id |= self.category_1
        self.assertFalse(self._get_old_value())
        self.assertEqual(self._get_new_value(), self.category_1.ids)
        self.partner.with_user(self.main_company_user).category_id |= self.category_3
        self.assertEqual(self._get_old_value(), self.category_1.ids)
        self.assertEqual(self._get_new_value(), (self.category_1 | self.category_3).ids)

        # self.partner.invalidate_recordset()
        self.partner.with_user(self.other_company_user).category_id |= self.category_2
        self.assertFalse(self._get_old_value())
        self.assertEqual(self._get_new_value(), self.category_2.ids)
        self.partner.with_user(self.other_company_user).category_id |= self.category_4
        self.assertEqual(self._get_old_value(), self.category_2.ids)
        self.assertEqual(self._get_new_value(), (self.category_2 | self.category_4).ids)

        # self.partner.invalidate_recordset()
        self.assertEqual(
            self.partner.with_user(self.main_company_user).category_id,
            (self.category_1 | self.category_3),
        )
        # self.partner.invalidate_recordset()
        self.assertEqual(
            self.partner.with_user(self.other_company_user).category_id,
            (self.category_2 | self.category_4),
        )
