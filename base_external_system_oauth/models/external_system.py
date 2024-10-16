# Copyright 2023 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ExternalSystem(models.Model):
    """Extend base external system"""

    _inherit = "external.system"

    oauth_definition_id = fields.Many2one(
        comodel_name="auth.oauth.provider",
        help="Use this if authorisation done by oauth provider",
    )
