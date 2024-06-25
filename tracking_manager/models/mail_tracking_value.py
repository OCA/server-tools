# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models

from ..tools import format_m2m


class MailTrackingValue(models.Model):
    _inherit = "mail.tracking.value"

    def create_tracking_values(
        self,
        initial_value,
        new_value,
        col_name,
        col_info,
        tracking_sequence
    ):
        if col_info["type"] == "many2many":
            col_info["type"] = "text"
            initial_value = format_m2m(initial_value)
            new_value = format_m2m(new_value)
        return super().create_tracking_values(
            initial_value, new_value, col_name, col_info, tracking_sequence
        )
