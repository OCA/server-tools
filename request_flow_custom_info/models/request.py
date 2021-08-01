# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class RequestRequest(models.Model):
    _name = "request.request"
    _inherit = [_name, "custom.info"]

    custom_info_template_id = fields.Many2one(context={"default_model": _name})
    custom_info_ids = fields.One2many(context={"default_model": _name})

    @api.onchange("category_id")
    def _onchange_category_id_custom_info(self):
        self.custom_info_template_id = self.category_id.custom_info_template_id
