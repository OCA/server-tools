# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

import sentry_sdk

_logger = logging.getLogger(__name__)

try:
    from odoo.addons.queue_job.controllers.main import RunJobController
except ImportError:
    _logger.debug("'queue_job' is not available, its jobs keep the default name.")
else:

    class SentryRunJobController(RunJobController):
        @classmethod
        def _runjob(cls, env, job):
            """Report a queue job under a name of its own.

            A job already runs inside an HTTP request, so the WSGI middleware
            gives it a scope of its own. What it does not give it is a name:
            every job is reported as the route that ran it, which groups all
            of them together whatever they were doing. Name it after the job
            instead, keeping to the model and the method so that jobs of the
            same kind still group together.
            """
            sentry_sdk.get_current_scope().set_transaction_name(
                f"{job.model_name}.{job.method_name}", source="task"
            )
            return super()._runjob(env, job)
