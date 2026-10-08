# Copyright 2026 Ledoent
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    sentry_client_replay_optout = fields.Boolean(
        string="Disable Sentry session replay",
        help="Sentry session replay records DOM changes, console activity, "
        "and network requests for any session that hits an error. "
        "Enable this to keep that recording off for your own sessions, "
        "regardless of the database-wide Tier 2 toggle. Server-wide error "
        "capture (Tier 0) is unaffected.",
    )

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + ["sentry_client_replay_optout"]

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + ["sentry_client_replay_optout"]
