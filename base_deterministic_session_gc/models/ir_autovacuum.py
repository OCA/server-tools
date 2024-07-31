# Copyright 2019 Trobz <https://trobz.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, http, models
from odoo.exceptions import AccessDenied


class AutoVacuum(models.AbstractModel):
    _inherit = "ir.autovacuum"

    @api.model
    def gc_sessions(self, session_expiry_delay=None):
        """
        Not overriding `power_on()` because we want:
        - our own scheduled action
        - our own public method (it can be useful to remotely
          force all sessions to expire via an api call)
        """

        if not self.env.user._is_admin():
            raise AccessDenied()

        http.deterministic_session_gc(http.root.session_store, session_expiry_delay)

        return True
