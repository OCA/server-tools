# Copyright 2024 Camptocamp SA
# @author Italo LOPES <italo.lopes@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    set_default_models = fields.Boolean(
        string="Set default models",
        help="Set the default models that should have noupdate=True.",
    )
    models_force_noupdate = fields.Many2many(
        "ir.model",
        string="Models to force noupdate=True",
        domain=[("transient", "=", False)],
    )

    def set_values(self):
        """
        Save the selected models in the system parameters as a comma-separated list.
        """
        res = super(ResConfigSettings, self).set_values()
        # get current values from the system parameters and set noupdate=False
        current_models_force_noupdate = (
            self.env["ir.config_parameter"].sudo().get_param("models_force_noupdate")
        )
        if current_models_force_noupdate:
            self._compare_values(current_models_force_noupdate)
        # save the selected models in the system parameters as a comma-separated list
        if self.models_force_noupdate:
            new_models_force_noupdate = ",".join(
                map(str, self.models_force_noupdate.ids)
            )
            self.env["ir.config_parameter"].sudo().set_param(
                "models_force_noupdate", new_models_force_noupdate
            )
            self._update_ir_model_data(self.models_force_noupdate)
        else:
            self.env["ir.config_parameter"].sudo().set_param(
                "models_force_noupdate", False
            )
        return res

    def _compare_values(self, current_models_force_noupdate):
        # convert the current values from the system parameters to a list of model IDs
        current_models_force_noupdate = list(
            map(int, current_models_force_noupdate.split(","))
        )
        if self.models_force_noupdate:
            self._update_ir_model_data(
                self.env["ir.model"].browse(
                    list(
                        set(current_models_force_noupdate)
                        - set(self.models_force_noupdate.ids)
                    )
                ),
                noupdate=False,
            )
        else:
            self._update_ir_model_data(
                self.env["ir.model"].browse(current_models_force_noupdate),
                noupdate=False,
            )

    def get_values(self):
        """
        Get the selected models from the system parameters as a comma-separated list.
        """
        res = super(ResConfigSettings, self).get_values()
        # get the selected models from the system parameters as a comma-separated list
        models_force_noupdate = (
            self.env["ir.config_parameter"].sudo().get_param("models_force_noupdate")
        )
        # convert the comma-separated list in a list of model IDs
        if models_force_noupdate:

            models_force_noupdate = self.env["ir.model"].browse(
                list(map(int, models_force_noupdate.split(",")))
            )
            res.update(models_force_noupdate=models_force_noupdate.ids)
        return res

    def _update_ir_model_data(self, to_update_models, noupdate=True):
        """
        Update the ir.model.data records for the selected models.
        """
        # get the selected models
        if not models:
            return
        # update the ir.model.data records for the selected models setting noupdate=True
        for model in to_update_models:
            self.env["ir.model.data"].search([("model", "=", model.model)]).write(
                {"noupdate": noupdate}
            )

    def _get_preset_noupdate_models(self):
        """
        Return a list of models that should have noupdate=True by default.
        """
        models_force_noupdate = [
            "res.lang",
            "ir.rules",
            "ir.model.access",
            "res.groups",
            "mail.template",
            "res.users.role",
        ]
        return self.env["ir.model"].search([("model", "in", models_force_noupdate)])

    @api.onchange("set_default_models")
    def onchange_set_default_models(self):
        """
        Prefill the field models_force_noupdate with the preset models.
        """
        default_models = self._get_preset_noupdate_models()
        current_models = self.models_force_noupdate

        if self.set_default_models:
            models_force_noupdate = [
                (4, model.id) for model in default_models + current_models
            ]
        else:
            models_force_noupdate = [(3, model.id) for model in default_models]
        self.models_force_noupdate = models_force_noupdate
