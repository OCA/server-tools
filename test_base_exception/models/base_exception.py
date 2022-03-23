# Copyright 2011 Raphaël Valyi, Renato Lima, Guewen Baconnier, Sodexis
# Copyright 2017 Akretion (http://www.akretion.com)
# Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# Copyright 2020 Hibou Corp.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ExceptionRule(models.Model):
    _inherit = "exception.rule"

    test_purchase_ids = fields.Many2many("base.exception.test.purchase")
    model = fields.Selection(
        selection_add=[
            ("base.exception.test.purchase", "Purchase Order"),
            ("base.exception.test.purchase.line", "Purchase Order Line"),
        ],
        ondelete={
            "base.exception.test.purchase": "cascade",
            "base.exception.test.purchase.line": "cascade",
        },
    )
