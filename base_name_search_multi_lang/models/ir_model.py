# Copyright 2020 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo import api, fields, models


class IrModel(models.Model):
    _inherit = "ir.model"

    name_search_multi_lang = fields.Boolean(
        string="Search Translated Name",
        help="Name search this model from all translated languages",
    )

    @api.constrains("name_search_multi_lang")
    def update_name_search_multi_lang(self):
        self.env.registry.clear_cache()
