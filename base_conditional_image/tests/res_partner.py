# Copyright 2023 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

from odoo import models


class ResPartner(models.Model):
    _inherit = ["res.partner", "conditional.image.consumer.mixin"]
    _name = "res.partner"
