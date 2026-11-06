# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import sentry_sdk

from odoo import models


class IrCron(models.Model):
    _inherit = "ir.cron"

    def _callback(self, cron_name, server_action_id):
        """Run every job under a scope of its own.

        The WSGI middleware gives each HTTP request a fresh scope, but a cron
        worker serves no request, so its jobs otherwise keep the scope that
        existed when ``sentry_sdk.init()`` ran: in the master process, before
        the workers forked. Events coming from unrelated jobs then report the
        same trace and carry each other's breadcrumbs.
        """
        with sentry_sdk.isolation_scope() as scope:
            # Forking a scope copies what is already on it, so the inherited
            # trace and breadcrumbs have to be dropped explicitly.
            scope.clear_breadcrumbs()
            scope.set_new_propagation_context()
            scope.set_transaction_name(cron_name, source="task")
            return super()._callback(cron_name, server_action_id)
