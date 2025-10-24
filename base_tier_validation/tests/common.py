# Copyright 2018-19 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo_test_helper import FakeModelLoader

from odoo import Command
from odoo.tests import new_test_user

from odoo.addons.base.tests.common import BaseCommon


class CommonTierValidation(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from .tier_validation_tester import (
            TierDefinition,
            TierValidationTester,
            TierValidationTester2,
            TierValidationTesterComputed,
        )

        cls.loader.update_registry(
            (
                TierValidationTester,
                TierValidationTester2,
                TierValidationTesterComputed,
                TierDefinition,
            )
        )

        cls.test_model = cls.env[TierValidationTester._name]
        cls.test_model_2 = cls.env[TierValidationTester2._name]
        cls.test_model_computed = cls.env[TierValidationTesterComputed._name]

        cls.tester_model = cls.env["ir.model"].search(
            [("model", "=", "tier.validation.tester")]
        )
        cls.tester_model_2 = cls.env["ir.model"].search(
            [("model", "=", "tier.validation.tester2")]
        )
        cls.tester_model_computed = cls.env["ir.model"].search(
            [("model", "=", "tier.validation.tester.computed")]
        )
        # Create a multi-company
        cls.main_company = cls.env.ref("base.main_company")
        cls.other_company = cls.env["res.company"].create({"name": "My Company"})

        models = (
            cls.tester_model,
            cls.tester_model_2,
            cls.tester_model_computed,
        )
        for model in models:
            # Access record:
            cls.env["ir.model.access"].create(
                {
                    "name": f"access {model.name}",
                    "model_id": model.id,
                    "perm_read": 1,
                    "perm_write": 1,
                    "perm_create": 1,
                    "perm_unlink": 1,
                }
            )

            # Define views to avoid automatic views with all fields.
            cls.env["ir.ui.view"].create(
                {
                    "model": model.model,
                    "name": f"Demo view for {model}",
                    "arch": """<form>
                    <header>
                        <button name="action_confirm" type="object" string="Confirm" />
                        <field name="state" widget="statusbar" />
                    </header>
                    <sheet>
                        <field name="test_field" />
                    </sheet>
                    </form>""",
                }
            )

        # Create users:
        cls.test_user_1 = new_test_user(
            cls.env, name="John", login="test1", groups="base.group_system"
        )
        cls.test_user_2 = new_test_user(cls.env, name="Mike", login="test2")
        cls.test_user_3_multi_company = new_test_user(
            cls.env,
            name="Jane",
            login="test3",
            company_ids=[Command.set([cls.main_company.id, cls.other_company.id])],
        )
        # Create tier definitions:
        cls.tier_def_obj = cls.env["tier.definition"]
        cls.tier_definition = cls.tier_def_obj.create(
            {
                "model_id": cls.tester_model.id,
                "review_type": "individual",
                "reviewer_id": cls.test_user_1.id,
                "definition_domain": "[('test_field', '=', 1.0)]",
                "sequence": 30,
            }
        )

        cls.test_record = cls.test_model.create({"test_field": 1.0})
        cls.test_record_2 = cls.test_model_2.create({"test_field": 1.0})
        cls.test_record_computed = cls.test_model_computed.create({"test_field": 1.0})

        cls.tier_def_obj.create(
            {
                "model_id": cls.tester_model.id,
                "review_type": "individual",
                "reviewer_id": cls.test_user_1.id,
                "definition_domain": "[('test_field', '>', 3.0)]",
                "approve_sequence": True,
                "notify_on_pending": False,
                "sequence": 20,
                "name": "Definition for test 19 - sequence - user 1",
            }
        )
        cls.tier_def_obj.create(
            {
                "model_id": cls.tester_model.id,
                "review_type": "individual",
                "reviewer_id": cls.test_user_2.id,
                "definition_domain": "[('test_field', '>', 3.0)]",
                "approve_sequence": True,
                "notify_on_pending": True,
                "sequence": 10,
                "name": "Definition for test 19 - sequence - user 2",
            }
        )
        # Create definition for test 20
        cls.tier_def_obj.create(
            {
                "model_id": cls.tester_model.id,
                "review_type": "individual",
                "reviewer_id": cls.test_user_1.id,
                "definition_domain": "[('test_field', '=', 0.9)]",
                "approve_sequence": False,
                "notify_on_pending": True,
                "sequence": 10,
                "name": "Definition for test 20 - no sequence -  user 1 - no sequence",
            }
        )

        cls.tier_def_obj.create(
            {
                "model_id": cls.tester_model_computed.id,
                "review_type": "individual",
                "reviewer_id": cls.test_user_1.id,
                "definition_domain": "[]",
                "approve_sequence": True,
                "notify_on_pending": False,
                "sequence": 20,
                "name": "Definition for computed model",
            }
        )

        # Create definition for test 30, 31
        # Main company tier definition
        cls.tier_def_obj.create(
            {
                "model_id": cls.tester_model_2.id,
                "review_type": "individual",
                "reviewer_id": cls.test_user_1.id,
                "definition_domain": "[('test_field', '>=', 1.0)]",
                "approve_sequence": True,
                "notify_on_pending": False,
                "sequence": 30,
                "name": "Definition for test 30 - sequence - user 1 - main company",
                "company_id": cls.main_company.id,
            }
        )
        cls.tier_def_obj.create(
            {
                "model_id": cls.tester_model_2.id,
                "review_type": "individual",
                "reviewer_id": cls.test_user_3_multi_company.id,
                "definition_domain": "[('test_field', '>=', 1.0)]",
                "approve_sequence": True,
                "notify_on_pending": False,
                "sequence": 20,
                "name": "Definition for test 30 - sequence - user 3 - main company",
                "company_id": cls.main_company.id,
            }
        )
        # Other company tier definition
        cls.tier_def_obj.create(
            {
                "model_id": cls.tester_model_2.id,
                "review_type": "individual",
                "reviewer_id": cls.test_user_3_multi_company.id,
                "definition_domain": "[('test_field', '>=', 1.0)]",
                "approve_sequence": True,
                "notify_on_pending": False,
                "sequence": 30,
                "name": "Definition for test 30 - sequence - user 3 - other company",
                "company_id": cls.other_company.id,
            }
        )

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super().tearDownClass()
