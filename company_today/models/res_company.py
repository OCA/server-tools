# SPDX-FileCopyrightText: 2022 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import api, fields, models


class Company(models.Model):
    _inherit = "res.company"

    today = fields.Date(
        string="Today's Date",
        default=lambda _: fields.Date.today(),
        readonly=True,
    )

    @api.model
    def cron_update_today(self):
        companies = self.search([])
        companies.write({"today": fields.Date.today()})
