# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResTerritory(models.Model):
    _name = "res.territory"
    _description = "Territory"

    name = fields.Char(string="Name", required=True)
    branch_id = fields.Many2one("res.branch", string="Branch")
    district_id = fields.Many2one(related="branch_id.district_id", string="District")
    region_id = fields.Many2one(
        related="branch_id.district_id.region_id", string="Region"
    )
    description = fields.Char(string="Description")
    type = fields.Selection(
        [("zip", "Zip"), ("state", "State"), ("country", "Country")], "Type"
    )
    zip_codes = fields.Char(string="ZIP Codes")
    country_ids = fields.One2many("res.country", "territory_id", string="Country Names")
