# Copyright 2023 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ExternalSystem(models.Model):
    """Extend base external system"""

    _inherit = "external.system"

    endpoint_ids = fields.One2many(
        comodel_name="external.system.endpoint",
        inverse_name="system_id",
        help="Endpoints on remote system",
    )
