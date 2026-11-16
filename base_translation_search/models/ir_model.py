# Copyright 2026 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo import api, fields, models


class IrModel(models.Model):
    _inherit = "ir.model"

    translation_search = fields.Boolean(
        help="Match the translated fields of this model in all the installed "
        "languages, in every search: search views, Many2one fields and domains",
    )

    @api.constrains("translation_search")
    def _check_translation_search(self):
        self.env.registry.clear_cache()
