# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestIrModel(TransactionCase):
    def _create_custom_model(self, **vals):
        model = self.env["ir.model"].create(
            dict({"name": "Kanban Custom", "model": "x_kanban_custom"}, **vals)
        )
        self._track_registry_attrs(model.model)
        return model

    def _track_registry_attrs(self, model_name):
        # the registry is updated in place when a custom model is set up
        self.attrs_before[model_name] = set(vars(type(self.env[model_name])))

    def test_reflect_kanban_model(self):
        model = self.env["ir.model"]._get("base.kanban.stage")
        self.assertFalse(model.is_kanban)

    def test_custom_model_becomes_kanban(self):
        model = self._create_custom_model()
        self.assertNotIn("stage_id", self.env[model.model]._fields)
        model.write({"is_kanban": True})
        self._track_registry_attrs(model.model)
        self.assertTrue(model.is_kanban)
        self.assertIn("stage_id", self.env[model.model]._fields)
        with self.assertRaises(UserError):
            model.write({"is_kanban": False})

    def test_custom_model_created_as_kanban(self):
        model = self._create_custom_model(is_kanban=True)
        self.assertIn("stage_id", self.env[model.model]._fields)

    def test_only_custom_models_can_become_kanban(self):
        model = self.env["ir.model"]._get("res.partner")
        with self.assertRaises(UserError):
            model.write({"is_kanban": True})

    def test_write_other_values(self):
        model = self._create_custom_model()
        model.write({"name": "Renamed"})
        self.assertEqual(model.name, "Renamed")
