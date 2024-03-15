# Copyright 2021 Akretion (http://www.akretion.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ResPartner(models.Model):
    _name = "res.partner"
    _inherits = ["res.partner", "restrict.edition.mixin"]
