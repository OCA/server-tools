# Copyright 2024 ForgeFlow S.L.
# License AGPL-3

from odoo.tests import Form, common, tagged


class Form(Form):
    def __init__(self, recordp, view=None):
        super().__init__(recordp, view)
        self._view["onchange"] = {k: "1" for k in self._view["onchange"].keys()}


@tagged("-at_install", "post_install")
class TestBaseOnchangeRule(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.rule_model = cls.env["base.onchange.rule"]
        cls.company_model = cls.env["res.company"]
        cls.model_model = cls.env["ir.model"]
        cls.field_model = cls.env["ir.model.fields"]
        cls.company_1 = cls.env.ref("base.main_company")
        cls.company_2 = cls.company_model.create({"name": "Company 2"})

    @classmethod
    def _get_field(cls, field_name, model):
        domain = [("model_id", "=", model), ("name", "=", field_name)]
        return cls.field_model.search(domain, limit=1)

    @classmethod
    def _get_model(cls, model):
        return cls.model_model.search([("model", "=", model)])

    @classmethod
    def _create_rule(cls, company_id=1, value="T"):
        cls.rule_model.create(
            {
                "name": "Test Rule",
                "model": cls._get_model("res.currency").id,
                "code": "res = records.filtered(lambda r: r.name == 'TST')",
                "onchange_fields": cls._get_field("name", "res.currency").ids,
                "company_id": company_id,
                "fields_lines": [
                    (
                        0,
                        0,
                        {
                            "col1": cls._get_field("symbol", "res.currency").id,
                            "value": value,
                            "evaluation_type": "value",
                        },
                    )
                ],
                "active": True,
            }
        )

    def test_01_rule_evaluation(self):
        self._create_rule(self.company_1.id, "T")
        self._create_rule(self.company_2.id, "S")
        with Form(
            self.env.ref("base.USD").with_context(company_id=self.company_1.id)
        ) as form:
            form.name = "TST"
            self.assertEqual(form.symbol, "T")
