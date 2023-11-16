# Copyright 2015-2017 Camptocamp SA
# Copyright 2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common
from odoo.tools import mute_logger


class TestChangesetFieldRule(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.company_model_id = self.env.ref("base.model_res_company").id
        self.field_name = self.env.ref("base.field_res_partner__name")
        self.field_street = self.env.ref("base.field_res_partner__street")

    @mute_logger("odoo.models.unlink")
    def test_get_rules(self):
        ChangesetFieldRule = self.env["changeset.field.rule"]
        ChangesetFieldRule.search([]).unlink()
        rule1 = ChangesetFieldRule.create(
            {"field_id": self.field_name.id, "action": "validate"}
        )
        rule2 = ChangesetFieldRule.create(
            {"field_id": self.field_street.id, "action": "never"}
        )
        get_rules = ChangesetFieldRule.get_rules(None, "res.partner")
        self.assertEqual(get_rules, {"name": rule1, "street": rule2})

    def test_get_rules_source(self):
        ChangesetFieldRule = self.env["changeset.field.rule"]
        ChangesetFieldRule.search([]).unlink()
        rule1 = ChangesetFieldRule.create(
            {"field_id": self.field_name.id, "action": "validate"}
        )
        rule2 = ChangesetFieldRule.create(
            {"field_id": self.field_street.id, "action": "never"}
        )
        rule3 = ChangesetFieldRule.create(
            {
                "source_model_id": self.company_model_id,
                "field_id": self.field_street.id,
                "action": "never",
            }
        )
        model = ChangesetFieldRule
        rules = model.get_rules(None, "res.partner")
        self.assertEqual(rules, {"name": rule1, "street": rule2})
        rules = model.get_rules("res.company", "res.partner")
        self.assertEqual(rules, {"name": rule1, "street": rule3})

    def test_get_rules_cache(self):
        ChangesetFieldRule = self.env["changeset.field.rule"]
        ChangesetFieldRule.search([]).unlink()
        rule = ChangesetFieldRule.create(
            {"field_id": self.field_name.id, "action": "validate"}
        )
        self.assertEqual(
            ChangesetFieldRule.get_rules(None, "res.partner")["name"].action, "validate"
        )
        # Write on cursor to bypass the cache invalidation for the
        # matter of the test
        self.env.cr.execute(
            "UPDATE changeset_field_rule " "SET action = 'never' " "WHERE id = %s",
            (rule.id,),
        )
        self.assertEqual(
            ChangesetFieldRule.get_rules(None, "res.partner")["name"].action, "validate"
        )
        rule.action = "auto"
        self.assertEqual(
            ChangesetFieldRule.get_rules(None, "res.partner")["name"].action, "auto"
        )
        rule.unlink()
        self.assertFalse(ChangesetFieldRule.get_rules(None, "res.partner"))
