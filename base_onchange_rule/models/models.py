# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, models


class BaseModel(models.BaseModel):
    _inherit = "base"

    @api.model
    def _get_dynamic_onchange_fields(self, model_name):
        return (
            self.env["base.onchange.rule"]
            .search([("model", "=", model_name)])
            .mapped("onchange_fields.name")
        )

    def _onchange_eval(self, field_name, onchange, result):
        """Dynamicaly add onchange trigger for fields specified in Onchange Rule

        See sale-workflow/sale_order_qty_change_no_recompute/models/sale_order.py
        for reasoning behind extending this function rather than any other.
        """
        res = super()._onchange_eval(field_name, onchange, result)
        onchange = onchange.strip()
        onchange_fields = self._get_dynamic_onchange_fields(self._name)
        if onchange in ("1", "true") and field_name in onchange_fields:
            self._run_onchange_rules(field_name)
        return res

    def _run_onchange_rules(self, field_name):
        """This function is triggered when the value of any of dynamically set
        onchange fields are changed in a sale.order.line
        """
        domain = [("onchange_fields.name", "=", field_name)]
        self.env["base.onchange.rule"].search(domain).evaluate_rules(self)
