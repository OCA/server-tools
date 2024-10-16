# Copyright 2023 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
"""Endpoint on remote system to get from or post to."""

from odoo import fields, models


class ExternalSystemEndpoint(models.Model):
    """Endpoint on remote system to get from or post to."""

    _name = "external.system.endpoint"
    _description = __doc__

    system_id = fields.Many2one(comodel_name="external.system", required=True)
    name = fields.Char(string="Logical name for endpoint", required=True)
    endpoint = fields.Char(
        required=True,
        help="Remote path to append to base url for endpoint",
    )
