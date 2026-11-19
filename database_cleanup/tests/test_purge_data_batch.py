# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import uuid

from odoo.tests.common import tagged

from .common import Common, environment

ORPHAN_COUNT = 12


# Use post_install to get all models loaded more info: odoo/odoo#13458
@tagged("post_install", "-at_install")
class TestCleanupPurgeWizardDataBatch(Common):
    def _create_orphans(self, env, count):
        """Create ``count`` data entries pointing to non existing users."""
        env.cr.execute("SELECT max(id) FROM res_users")
        max_id = env.cr.fetchone()[0]
        prefix = f"test_batch_orphan_{uuid.uuid4().hex[:8]}"
        env["ir.model.data"].create(
            [
                {
                    "module": "database_cleanup",
                    "name": f"{prefix}_{i}",
                    "model": "res.users",
                    "res_id": max_id + 1000 + i,
                }
                for i in range(count)
            ]
        )
        return prefix

    def test_find_progress_lines(self):
        with environment() as env:
            self._create_orphans(env, ORPHAN_COUNT)
            wizard = env["cleanup.purge.wizard.data.batch"].create({})
            user_line = wizard.line_ids.filtered(lambda line: line.model == "res.users")
            self.assertTrue(user_line)
            self.assertGreaterEqual(user_line.orphan_count, ORPHAN_COUNT)
            self.assertEqual(
                wizard.orphan_count, sum(wizard.line_ids.mapped("orphan_count"))
            )
            self.assertEqual(
                wizard.remaining_count,
                wizard.orphan_count - wizard.purged_count,
            )
            self.assertFalse(wizard.done)

    def test_purge_single_batch(self):
        with environment() as env:
            self._create_orphans(env, ORPHAN_COUNT)
            wizard = env["cleanup.purge.wizard.data.batch"].create({"batch_size": 5})
            remaining_before = wizard.remaining_count
            purged = wizard._purge_batch()
            self.assertEqual(purged, 5)
            self.assertEqual(wizard.purged_count, 5)
            self.assertEqual(wizard.remaining_count, remaining_before - 5)
            # the batch is not committed by _purge_batch itself
            env.cr.commit()  # pylint: disable=invalid-commit
            self.assertEqual(
                env["cleanup.purge.wizard.data.batch"].browse(wizard.id).purged_count,
                5,
            )

    def test_purge_all_in_batches(self):
        with environment() as env:
            prefix = self._create_orphans(env, ORPHAN_COUNT)
            wizard = env["cleanup.purge.wizard.data.batch"].create({"batch_size": 5})
            wizard.action_purge_all()
            self.assertEqual(wizard.remaining_count, 0)
            self.assertTrue(wizard.done)
            self.assertEqual(wizard.progress, 100.0)
            self.assertTrue(all(wizard.line_ids.mapped("done")))
            # must be removed by the wizard
            with self.assertRaises(ValueError):
                env.ref(f"database_cleanup.{prefix}_0")
            with self.assertRaises(ValueError):
                env.ref(f"database_cleanup.{prefix}_{ORPHAN_COUNT - 1}")
