# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class IrActionsServer(models.Model):
    _inherit = "ir.actions.server"

    failure_count = fields.Integer(
        default=0,
        readonly=True,
        help="Number of consecutive failures of the related scheduled action.",
    )
