from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"
    _exclude_restrict_models = [
        "ir.model",
        "ir.config_parameter",
        "res.config.settings",
        "res.users",
    ]

    restrict_update_method = fields.Selection(
        selection=[
            ("model", "Model Restriction"),
            ("user", "User Restriction"),
        ],
        string="Extra Restriction Method",
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        # If all model is restricted, consider as user restriction
        non_restrict_count = self.env["ir.model"].search_count(
            [
                ("model", "not in", self._exclude_restrict_models),
                ("restrict_update", "=", False),
            ]
        )
        if non_restrict_count == 0:
            res["restrict_update_method"] = "user"
        else:
            res["restrict_update_method"] = "model"
        return res

    @api.model
    def set_values(self):
        super().set_values()
        prev_method = self.get_values().get("restrict_update_method")
        excludes = ["ir.model", "ir.config_parameter"]
        # If method changed, reset models and users
        if prev_method != self.restrict_update_method:
            all_models = self.env["ir.model"].search(
                [
                    ("model", "not in", self._exclude_restrict_models),
                    ("model", "not in", excludes),
                ]
            )
            all_users = self.env["res.users"].search([])
            if self.restrict_update_method == "model":
                all_models.write({"restrict_update": False})
                all_users.write({"unrestrict_model_update": False})
            if self.restrict_update_method == "user":
                all_models.write({"restrict_update": True})
                all_users.write({"unrestrict_model_update": True})
