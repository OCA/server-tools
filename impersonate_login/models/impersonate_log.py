# Copyright (C) 2024 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class ImpersonateLog(models.Model):
    _name = "impersonate.log"
    _description = "Impersonate Logs"

    user_id = fields.Many2one(
        comodel_name="res.partner",
        string="User",
    )
    impersonated_user_id = fields.Many2one(
        comodel_name="res.partner",
        string="Logged as",
    )
    date_start = fields.Datetime(
        string="Start Date",
    )
    date_end = fields.Datetime(
        string="End Date",
    )
