# Copyright 2024 Camptocamp SA
# @author Italo LOPES <italo.lopes@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests import TransactionCase


class BaseForceRecordNoupdate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(BaseForceRecordNoupdate, cls).setUpClass()
        cls.model_lang_str = "res.lang"
        cls.default_lang = cls.env.ref("base.lang_en")
        cls.system_parameter = cls.env["ir.config_parameter"]
        cls.noupdate_parameter_key = "models_force_noupdate"
        cls.config_settings = cls.env["res.config.settings"].sudo().create({})
        cls.default_models = cls.config_settings._get_preset_noupdate_models()

    def test_01_set_default_models(self):
        """
        Test if the default models are set correctly in the system parameters.
        """
        self.config_settings.set_default_models = True
        self.config_settings.onchange_set_default_models()
        self.config_settings.set_values()
        self.assertTrue(
            self.system_parameter.get_param(self.noupdate_parameter_key),
            "The system parameter should have been set",
        )
        # test if the models are set correctly in the system parameters
        parameter_values = list(
            map(
                int,
                self.system_parameter.get_param(self.noupdate_parameter_key).split(","),
            )
        )
        self.assertEqual(
            parameter_values,
            self.default_models.ids,
            "The default models should have been set",
        )

    def test_02_unset_default_models(self):
        """
        Test if the default models are unset correctly in the system parameters.
        """
        self.config_settings.set_default_models = False
        self.config_settings.set_values()
        self.assertFalse(
            self.system_parameter.get_param(self.noupdate_parameter_key),
            "The system parameter should have been unset",
        )

    def test_03_add_module_to_models_force_noupdate(self):
        """
        Test if a module is added to the 'models_force_noupdate' field
        and if the ir.model.data records are updated accordingly.
        """
        model_lang_id = self.env["ir.model"].search(
            [("model", "=", self.model_lang_str)], limit=1
        )
        self.assertTrue(
            model_lang_id,
            "The model should exist",
        )
        self.config_settings.models_force_noupdate = [(4, model_lang_id.id)]
        self.config_settings.set_values()
        self.assertTrue(
            self.system_parameter.get_param(self.noupdate_parameter_key),
            "The system parameter should have been set",
        )
        parameter_values = list(
            map(
                int,
                self.system_parameter.get_param(self.noupdate_parameter_key).split(","),
            )
        )
        self.assertIn(
            model_lang_id.id,
            parameter_values,
            "The model should have been added to the system parameters",
        )
        # test if any ir.model.data for the model has been updated
        ir_model_data = self.env["ir.model.data"].search(
            [("model", "=", self.model_lang_str)], limit=1
        )
        self.assertTrue(
            ir_model_data.noupdate,
            "The ir.model.data records should have been updated",
        )

    def test_04_remove_module_from_models_force_noupdate(self):
        """
        Test if when a module is removed from the 'models_force_noupdate' field
        the ir.model.data records are updated accordingly.
        """
        model_lang_id = self.env["ir.model"].search(
            [("model", "=", self.model_lang_str)], limit=1
        )
        ir_model_data = self.env["ir.model.data"].search(
            [("model", "=", self.model_lang_str)], limit=1
        )

        self.assertFalse(
            self.system_parameter.get_param(self.noupdate_parameter_key),
            "The system parameter is empty",
        )

        self.config_settings.models_force_noupdate = [(4, model_lang_id.id)]
        self.config_settings.set_values()

        self.assertTrue(
            self.system_parameter.get_param(self.noupdate_parameter_key),
            "The system parameter should have been set",
        )

        self.config_settings.models_force_noupdate = [(3, model_lang_id.id)]
        self.config_settings.set_values()
        self.assertFalse(
            self.system_parameter.get_param(self.noupdate_parameter_key),
            "The system parameter should have been removed",
        )

        # test if any ir.model.data for the model has been updated
        self.assertFalse(
            ir_model_data.noupdate,
            "The ir.model.data records should have been updated and be False",
        )
