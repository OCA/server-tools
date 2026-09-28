# Copyright 2026 KMEE INFORMATICA LTDA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import os
from unittest.mock import patch

from odoo.tests.common import TransactionCase

from odoo.addons.base_field_trigger_warmup.models.base_field_trigger_warmup import (
    ENV_DISABLE,
)


class TestFieldTriggerWarmup(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warmup = cls.env["base.field.trigger.warmup"]
        cls.param = cls.env["ir.config_parameter"].sudo()

    def test_warms_up_the_requested_models(self):
        """Every field of the given models has its trigger tree built."""
        built = []
        with patch.object(
            type(self.env.registry),
            "get_field_trigger_tree",
            side_effect=lambda field: built.append(field),
        ):
            count = self.warmup._warmup_field_trigger_trees(["res.partner"])
        self.assertEqual(count, len(self.env["res.partner"]._fields))
        self.assertEqual(count, len(built))

    def test_a_failing_field_does_not_break_the_warmup(self):
        """A field whose tree cannot be built is skipped, not raised."""
        partner_fields = list(self.env["res.partner"]._fields.values())
        broken = partner_fields[0]

        def build(field):
            if field is broken:
                raise ValueError("cannot build this one")

        with patch.object(
            type(self.env.registry), "get_field_trigger_tree", side_effect=build
        ):
            count = self.warmup._warmup_field_trigger_trees(["res.partner"])
        self.assertEqual(count, len(partner_fields) - 1)

    def test_missing_orm_api_is_a_no_op(self):
        """An Odoo build without the private method must not break."""
        registry_type = type(self.env.registry)
        with patch.object(registry_type, "get_field_trigger_tree", None, create=True):
            self.assertEqual(
                self.warmup._warmup_field_trigger_trees(["res.partner"]), 0
            )

    def test_scope_defaults_to_every_model(self):
        self.param.set_param("base_field_trigger_warmup.models", "*")
        self.assertEqual(
            sorted(self.warmup._warmup_model_names()),
            sorted(self.env.registry),
        )

    def test_scope_can_be_narrowed(self):
        self.param.set_param(
            "base_field_trigger_warmup.models", "res.partner, res.users"
        )
        self.assertEqual(
            sorted(self.warmup._warmup_model_names()),
            ["res.partner", "res.users"],
        )

    def test_unknown_models_are_ignored(self):
        self.param.set_param(
            "base_field_trigger_warmup.models", "res.partner,no.such.model"
        )
        self.assertEqual(self.warmup._warmup_model_names(), ["res.partner"])

    def test_enabled_by_default(self):
        with patch.object(type(self.env.registry), "in_test_mode", return_value=False):
            self.assertTrue(self.warmup._warmup_is_enabled())

    def test_disabled_in_test_mode(self):
        with patch.object(type(self.env.registry), "in_test_mode", return_value=True):
            self.assertFalse(self.warmup._warmup_is_enabled())

    def test_disabled_by_environment_variable(self):
        with patch.dict(os.environ, {ENV_DISABLE: "0"}), patch.object(
            type(self.env.registry), "in_test_mode", return_value=False
        ):
            self.assertFalse(self.warmup._warmup_is_enabled())
