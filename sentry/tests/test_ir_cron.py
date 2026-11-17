# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest.mock import patch

import sentry_sdk

from odoo.tests import TransactionCase

from odoo.addons.base.models.ir_cron import IrCron


class TestIrCronScope(TransactionCase):
    def _run_two_jobs(self):
        """Run two jobs, reporting the scope each one ran under."""
        seen = []

        def spy(self, cron_name, server_action_id):
            sentry_sdk.add_breadcrumb(message=cron_name)
            scope = sentry_sdk.get_isolation_scope()
            seen.append((scope.get_traceparent(), len(scope._breadcrumbs)))
            return True

        with patch.object(IrCron, "_callback", spy):
            self.env["ir.cron"]._callback("job-1", 1)
            self.env["ir.cron"]._callback("job-2", 2)
        return seen

    def test_each_job_runs_under_its_own_trace(self):
        outside = sentry_sdk.get_isolation_scope().get_traceparent()
        seen = self._run_two_jobs()
        self.assertEqual(len(seen), 2)
        self.assertTrue(
            all(traceparent for traceparent, _ in seen),
            "a job ran without any trace at all",
        )
        self.assertNotEqual(
            seen[0][0],
            seen[1][0],
            "both jobs reported the same trace, so they shared a scope",
        )
        self.assertEqual(
            sentry_sdk.get_isolation_scope().get_traceparent(),
            outside,
            "the scope of the worker itself must be left as it was",
        )

    def test_breadcrumbs_do_not_leak_between_jobs(self):
        seen = self._run_two_jobs()
        self.assertEqual(
            [count for _, count in seen],
            [1, 1],
            "a job saw breadcrumbs left by another one",
        )
