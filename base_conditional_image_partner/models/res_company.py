# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    logo = fields.Binary(readonly=True)
