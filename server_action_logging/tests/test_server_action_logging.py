import logging

from odoo.tests.common import TransactionCase


class TestServerActionLogging(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.action_no_sql_log = cls.env["ir.actions.server"].create(
            {
                "name": "Test Action w/o SQL Logging",
                "enable_sql_debug": False,
                "state": "code",
                "model_id": cls.env.ref("base.model_res_users").id,
                "model_name": "res.users",
                "code": "model.sudo().search([]).read(['name', 'login'])",
            }
        )
        cls.action_with_sql_log = cls.env["ir.actions.server"].create(
            {
                "name": "Test Action w/ SQL Logging",
                "enable_sql_debug": True,
                "state": "code",
                "model_id": cls.env.ref("base.model_res_users").id,
                "model_name": "res.users",
                "code": "model.sudo().search([]).read(['name', 'login'])",
            }
        )
        cls.action_with_error = cls.env["ir.actions.server"].create(
            {
                "name": "Test Action w/ Error",
                "enable_sql_debug": False,
                "state": "code",
                "model_id": cls.env.ref("base.model_res_users").id,
                "model_name": "res.users",
                "code": "model.sudo().search([]).read(['invalid_field'])",
            }
        )
        cls.log_action = logging.getLogger(
            "odoo.addons.server_action_logging.models.ir_actions_server"
        )
        cls.log_sql_db = logging.getLogger("odoo.sql_db")

    def setUp(self):
        super().setUp()
        # Odoo logger may be disabled for level ``logging.INFO`` when running tests
        if not self.log_action.isEnabledFor(logging.INFO):
            self.log_action.setLevel(logging.INFO)

    def test_00_log_action_timing(self):
        """Tests Odoo logs while running an action"""
        self.assertTrue(self.log_action.isEnabledFor(logging.INFO))
        self.assertFalse(self.log_sql_db.isEnabledFor(logging.DEBUG))
        with self.assertLogs(self.log_action, logging.INFO) as log_action_watcher:
            self.action_no_sql_log.run()
        self.assertFalse(self.log_sql_db.isEnabledFor(logging.DEBUG))
        logs = log_action_watcher.output
        self.assertEqual(len(logs), 2)
        self.assertEqual(
            f"INFO:{self.log_action.name}:Action {self.action_no_sql_log.display_name}"
            f" ({self.action_no_sql_log}) started",
            logs[0],
        )
        self.assertIn(
            f"INFO:{self.log_action.name}:Action {self.action_no_sql_log.display_name}"
            f" ({self.action_no_sql_log}) completed in",
            logs[1],
        )

    def test_01_log_action_sql_db(self):
        """Tests SQL logs while running an action"""
        self.assertTrue(self.log_action.isEnabledFor(logging.INFO))
        self.assertFalse(self.log_sql_db.isEnabledFor(logging.DEBUG))
        with self.assertLogs(self.log_sql_db, logging.DEBUG) as log_sql_db_watcher:
            # NB: ``self.assertLogs`` will automatically enable the ``logging.DEBUG``
            # level for the ``odoo.sql_db`` logger, which would make it impossible to
            # check whether the logging is dynamically enabled for actions which
            # require it; therefore, we manually disable the logger before executing
            # the action itself
            self.log_sql_db.setLevel(logging.NOTSET)
            self.action_with_sql_log.run()
        self.assertFalse(self.log_sql_db.isEnabledFor(logging.DEBUG))
        self.assertGreaterEqual(len(log_sql_db_watcher.output), 1)

    def test_02_log_action_failure(self):
        """Tests Odoo logs while running an action that fails"""
        self.assertTrue(self.log_action.isEnabledFor(logging.INFO))
        self.assertFalse(self.log_sql_db.isEnabledFor(logging.DEBUG))
        with self.assertLogs(self.log_action, logging.INFO) as log_action_watcher:
            with self.assertRaises(ValueError):
                self.action_with_error.run()
        self.assertFalse(self.log_sql_db.isEnabledFor(logging.DEBUG))
        logs = log_action_watcher.output
        self.assertEqual(len(logs), 1)
        self.assertEqual(
            f"INFO:{self.log_action.name}:Action {self.action_with_error.display_name}"
            f" ({self.action_with_error}) started",
            logs[0],
        )
