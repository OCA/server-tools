# Copyright 2019-2026  Vauxoo,Therp Bv (<http://www.vauxoo.com/>, <https://www.therp.nl/>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    @api.model
    def _index(self, *args, **kwargs):
        return False
