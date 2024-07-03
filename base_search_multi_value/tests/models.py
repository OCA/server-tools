from odoo import api, models


class ResPartner(models.Model):
    _inherit = ["res.partner", "search.multi.value.mixin"]
    _name = "res.partner"

    @api.model
    def _get_search_fields(self):
        return ["name", "email"]
