# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    user_tech_id = fields.Many2one(
        comodel_name="res.users",
        string="Technical User",
        help="This user can be used by process for technical purpose",
        domain="[('company_id', '=', id)]",
    )
