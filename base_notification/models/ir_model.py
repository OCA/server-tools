from odoo import api, models


class BaseModel(models.AbstractModel):
    _inherit = "base"

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        self.env["base.notification.rule"].sudo()._apply_trigger("on_create", records)
        return records

    def write(self, vals):
        res = super().write(vals)
        self.env["base.notification.rule"].sudo()._apply_trigger("on_write", self)
        return res

    def unlink(self):
        self.env["base.notification.rule"].sudo()._apply_trigger("on_unlink", self)
        return super().unlink()
