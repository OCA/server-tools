# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class IrMailServer(models.Model):

    _inherit = "ir.mail_server"

    recipients_min = fields.Integer(
        "Minimum number of recipients",
        help="Minimum number of recipients needed to use this server.",
    )

    _sql_constraints = [
        (
            "number_of_recipients_min_positive_check",
            "CHECK(recipients_min > 0)",
            "The minimum number of recipients has to be positive.",
        )
    ]
