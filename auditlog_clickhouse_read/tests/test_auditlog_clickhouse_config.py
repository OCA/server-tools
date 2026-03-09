# Copyright (C) 2026 Cetmix OÜ
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo.exceptions import UserError
from odoo.tests import tagged

from .common import AuditlogClickhouseReadCommon


class DummyPrivilegeError(Exception):
    pgcode = "42501"


@tagged("-at_install", "post_install")
class TestAuditlogClickhouseReadHelpers(AuditlogClickhouseReadCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.config = cls.create_config(is_active=True)

    def test_01_relation_kind_returns_none_when_relation_missing(self):
        with (
            patch.object(self.env.cr, "execute"),
            patch.object(self.env.cr, "fetchone", side_effect=[(None,)]),
        ):
            kind = self.config._relation_kind("public", "auditlog_log")

        self.assertIsNone(kind)

    def test_02_relation_kind_returns_pg_class_kind(self):
        with (
            patch.object(self.env.cr, "execute") as execute,
            patch.object(
                self.env.cr,
                "fetchone",
                side_effect=[("public.auditlog_log",), ("f",)],
            ),
        ):
            kind = self.config._relation_kind("public", "auditlog_log")

        self.assertEqual(kind, "f")
        self.assertEqual(execute.call_count, 2)

    def test_03_get_auditlog_read_mode_fdw(self):
        with patch.object(
            type(self.config),
            "_relation_kind",
            autospec=True,
            side_effect=["f", "f"],
        ):
            self.assertEqual(self.config._get_auditlog_read_mode(), "fdw")

    def test_04_get_auditlog_read_mode_postgres(self):
        with patch.object(
            type(self.config),
            "_relation_kind",
            autospec=True,
            side_effect=["r", "r"],
        ):
            self.assertEqual(self.config._get_auditlog_read_mode(), "postgres")

    def test_05_get_auditlog_read_mode_mixed(self):
        with patch.object(
            type(self.config),
            "_relation_kind",
            autospec=True,
            side_effect=["r", "f"],
        ):
            self.assertEqual(self.config._get_auditlog_read_mode(), "mixed")

    def test_06_backup_helpers(self):
        with patch.object(
            type(self.config),
            "_relation_kind",
            autospec=True,
            side_effect=["r", "r", None, "r"],
        ):
            self.assertTrue(self.config._backup_tables_exist())
            self.assertTrue(self.config._any_backup_object_exists())

    def test_07_describe_relation_kind(self):
        self.assertEqual(self.config._describe_relation_kind(None), "missing")
        self.assertEqual(self.config._describe_relation_kind("r"), "regular table")
        self.assertEqual(self.config._describe_relation_kind("f"), "foreign table")
        self.assertEqual(self.config._describe_relation_kind("v"), "view")
        self.assertIn("unexpected relation", self.config._describe_relation_kind("x"))

    def test_08_raise_inconsistent_schema_state(self):
        with patch.object(
            type(self.config),
            "_relation_kind",
            autospec=True,
            side_effect=["r", "f", None, "r"],
        ):
            with self.assertRaises(UserError) as err:
                self.config._raise_inconsistent_schema_state()

        message = str(err.exception)
        self.assertIn(
            "Auditlog read mode is in an inconsistent PostgreSQL state", message
        )
        self.assertIn("auditlog_log", message)
        self.assertIn("auditlog_log_line", message)

    def test_09_raise_fdw_setup_error_privileges(self):
        with self.assertRaises(UserError) as err:
            self.config._raise_fdw_setup_error(
                "Failed to create or update the FDW server",
                DummyPrivilegeError("permission denied"),
            )

        message = str(err.exception)
        self.assertIn(
            "The current PostgreSQL user does not have enough privileges", message
        )
        self.assertIn("clickhouse_fdw", message)
        self.assertIn("auditlog_clickhouse_srv", message)

    def test_10_raise_fdw_setup_error_generic(self):
        with self.assertRaises(UserError) as err:
            self.config._raise_fdw_setup_error(
                "Failed to create or update the FDW server",
                Exception("boom"),
            )

        self.assertIn("Failed to create or update the FDW server", str(err.exception))
        self.assertIn("boom", str(err.exception))


@tagged("-at_install", "post_install")
class TestAuditlogClickhouseReadProtection(AuditlogClickhouseReadCommon):
    def test_01_deactivate_blocked_when_fdw_enabled(self):
        config = self.create_config(is_active=True)
        config.write({"fdw_enabled": True})

        with self.assertRaises(UserError):
            config.write({"is_active": False})

    def test_02_connection_change_blocked_when_fdw_enabled(self):
        config = self.create_config(is_active=True)
        config.write({"fdw_enabled": True})

        with self.assertRaises(UserError):
            config.write({"host": "clickhouse.internal"})

        with self.assertRaises(UserError):
            config.write({"database": "other_db"})

    def test_03_activation_blocked_if_other_fdw_config_exists(self):
        config_1 = self.create_config(is_active=True, host="h1")
        config_1.write({"fdw_enabled": True})

        config_2 = self.create_config(is_active=False, host="h2")

        with self.assertRaises(UserError):
            config_2.write({"is_active": True})

    def test_04_unlink_blocked_when_fdw_enabled(self):
        config = self.create_config(is_active=True)
        config.write({"fdw_enabled": True})

        with self.assertRaises(UserError):
            config.unlink()


@tagged("-at_install", "post_install")
class TestAuditlogClickhouseReadActions(AuditlogClickhouseReadCommon):
    def test_01_enable_requires_active_config(self):
        config = self.create_config(is_active=False)

        with self.assertRaises(UserError):
            config.action_enable_fdw_read()

    def test_02_enable_is_idempotent_when_already_fdw(self):
        config = self.create_config(is_active=True)

        with patch.object(
            type(config),
            "_get_auditlog_read_mode",
            autospec=True,
            return_value="fdw",
        ):
            action = config.action_enable_fdw_read()

        config.invalidate_recordset()
        self.assertTrue(config.fdw_enabled)
        self.assertEqual(action["params"]["type"], "info")

    def test_03_enable_rejects_mixed_state(self):
        config = self.create_config(is_active=True)

        with patch.object(
            type(config),
            "_get_auditlog_read_mode",
            autospec=True,
            return_value="mixed",
        ):
            with self.assertRaises(UserError):
                config.action_enable_fdw_read()

    def test_04_enable_rejects_stale_backup_objects(self):
        config = self.create_config(is_active=True)

        with (
            patch.object(
                type(config),
                "_get_auditlog_read_mode",
                autospec=True,
                return_value="postgres",
            ),
            patch.object(
                type(config),
                "_any_backup_object_exists",
                autospec=True,
                return_value=True,
            ),
        ):
            with self.assertRaises(UserError):
                config.action_enable_fdw_read()

    def test_05_enable_success_path(self):
        config = self.create_config(is_active=True)

        with (
            patch.object(
                type(config),
                "_get_auditlog_read_mode",
                autospec=True,
                return_value="postgres",
            ),
            patch.object(
                type(config),
                "_any_backup_object_exists",
                autospec=True,
                return_value=False,
            ),
            patch.object(
                type(config),
                "_ensure_pg_clickhouse_extension",
                autospec=True,
            ) as ensure_extension,
            patch.object(
                type(config),
                "_create_or_update_fdw_server",
                autospec=True,
            ) as update_server,
            patch.object(
                type(config),
                "_create_or_update_fdw_user_mapping",
                autospec=True,
            ) as update_mapping,
            patch.object(
                type(config),
                "_swap_auditlog_tables_to_fdw",
                autospec=True,
            ) as swap_tables,
            patch.object(
                type(config),
                "_healthcheck_fdw_read",
                autospec=True,
            ) as healthcheck,
        ):
            action = config.action_enable_fdw_read()

        config.invalidate_recordset()
        self.assertTrue(config.fdw_enabled)
        self.assertEqual(action["params"]["type"], "success")
        ensure_extension.assert_called_once_with(config)
        update_server.assert_called_once_with(config)
        update_mapping.assert_called_once_with(config)
        swap_tables.assert_called_once_with(config)
        healthcheck.assert_called_once_with(config)

    def test_06_enable_healthcheck_failure_keeps_flag_false(self):
        config = self.create_config(is_active=True)

        with (
            patch.object(
                type(config),
                "_get_auditlog_read_mode",
                autospec=True,
                return_value="postgres",
            ),
            patch.object(
                type(config),
                "_any_backup_object_exists",
                autospec=True,
                return_value=False,
            ),
            patch.object(
                type(config),
                "_ensure_pg_clickhouse_extension",
                autospec=True,
            ),
            patch.object(
                type(config),
                "_create_or_update_fdw_server",
                autospec=True,
            ),
            patch.object(
                type(config),
                "_create_or_update_fdw_user_mapping",
                autospec=True,
            ),
            patch.object(
                type(config),
                "_swap_auditlog_tables_to_fdw",
                autospec=True,
            ),
            patch.object(
                type(config),
                "_healthcheck_fdw_read",
                autospec=True,
                side_effect=UserError("healthcheck failed"),
            ),
        ):
            with self.assertRaises(UserError):
                config.action_enable_fdw_read()

        config.invalidate_recordset()
        self.assertFalse(config.fdw_enabled)

    def test_07_disable_is_idempotent_when_already_postgres(self):
        config = self.create_config(is_active=True)
        config.write({"fdw_enabled": True})

        with patch.object(
            type(config),
            "_get_auditlog_read_mode",
            autospec=True,
            return_value="postgres",
        ):
            action = config.action_disable_fdw_read()

        config.invalidate_recordset()
        self.assertFalse(config.fdw_enabled)
        self.assertEqual(action["params"]["type"], "info")

    def test_08_disable_rejects_mixed_state(self):
        config = self.create_config(is_active=True)
        config.write({"fdw_enabled": True})

        with patch.object(
            type(config),
            "_get_auditlog_read_mode",
            autospec=True,
            return_value="mixed",
        ):
            with self.assertRaises(UserError):
                config.action_disable_fdw_read()

    def test_09_disable_rejects_missing_backups(self):
        config = self.create_config(is_active=True)
        config.write({"fdw_enabled": True})

        with (
            patch.object(
                type(config),
                "_get_auditlog_read_mode",
                autospec=True,
                return_value="fdw",
            ),
            patch.object(
                type(config),
                "_backup_tables_exist",
                autospec=True,
                return_value=False,
            ),
        ):
            with self.assertRaises(UserError):
                config.action_disable_fdw_read()

    def test_10_disable_success_path(self):
        config = self.create_config(is_active=True)
        config.write({"fdw_enabled": True})

        with (
            patch.object(
                type(config),
                "_get_auditlog_read_mode",
                autospec=True,
                return_value="fdw",
            ),
            patch.object(
                type(config),
                "_backup_tables_exist",
                autospec=True,
                return_value=True,
            ),
            patch.object(
                type(config),
                "_restore_auditlog_tables_from_backup",
                autospec=True,
            ) as restore_tables,
        ):
            action = config.action_disable_fdw_read()

        config.invalidate_recordset()
        self.assertFalse(config.fdw_enabled)
        self.assertEqual(action["params"]["type"], "success")
        restore_tables.assert_called_once_with(config)


@tagged("-at_install", "post_install")
class TestAuditlogClickhouseReadDDLHelpers(AuditlogClickhouseReadCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.config = cls.create_config(is_active=True)

    def test_01_drop_foreign_table_if_exists(self):
        with (
            patch.object(
                type(self.config),
                "_relation_kind",
                autospec=True,
                return_value="f",
            ),
            patch.object(self.env.cr, "execute") as execute,
        ):
            self.config._drop_foreign_table_if_exists("public", "auditlog_log")

        execute.assert_called_once()

    def test_02_drop_foreign_table_skips_non_fdw_relation(self):
        with (
            patch.object(
                type(self.config),
                "_relation_kind",
                autospec=True,
                return_value="r",
            ),
            patch.object(self.env.cr, "execute") as execute,
        ):
            self.config._drop_foreign_table_if_exists("public", "auditlog_log")

        execute.assert_not_called()

    def test_03_rename_table_if_exists(self):
        with (
            patch.object(
                type(self.config),
                "_relation_kind",
                autospec=True,
                return_value="r",
            ),
            patch.object(self.env.cr, "execute") as execute,
        ):
            self.config._rename_table_if_exists(
                "public",
                "auditlog_log",
                "auditlog_log_pg_backup",
            )

        execute.assert_called_once()

    def test_04_rename_table_skips_non_regular_relation(self):
        with (
            patch.object(
                type(self.config),
                "_relation_kind",
                autospec=True,
                return_value="f",
            ),
            patch.object(self.env.cr, "execute") as execute,
        ):
            self.config._rename_table_if_exists(
                "public",
                "auditlog_log",
                "auditlog_log_pg_backup",
            )

        execute.assert_not_called()

    def test_05_drop_view_if_exists(self):
        with patch.object(self.env.cr, "execute") as execute:
            self.config._drop_view_if_exists("public", "auditlog_log_line_view")

        execute.assert_called_once()

    def test_06_ensure_sequences(self):
        with patch.object(self.env.cr, "execute") as execute:
            self.config._ensure_sequences()

        self.assertEqual(execute.call_count, 2)

    def test_07_create_foreign_tables(self):
        _ = self.config.database

        with patch.object(self.env.cr, "execute") as execute:
            self.config._create_foreign_tables("public")

        self.assertEqual(execute.call_count, 2)

    def test_08_recreate_auditlog_log_line_view(self):
        with (
            patch.object(
                type(self.config),
                "_drop_view_if_exists",
                autospec=True,
            ) as drop_view,
            patch.object(self.env.cr, "execute") as execute,
        ):
            self.config._recreate_auditlog_log_line_view("public")

        drop_view.assert_called_once_with(
            self.config, "public", "auditlog_log_line_view"
        )
        execute.assert_called_once()

    def test_09_swap_auditlog_tables_to_fdw_calls_expected_helpers(self):
        with (
            patch.object(
                type(self.config),
                "_drop_view_if_exists",
                autospec=True,
            ) as drop_view,
            patch.object(
                type(self.config),
                "_drop_foreign_table_if_exists",
                autospec=True,
            ) as drop_foreign,
            patch.object(
                type(self.config),
                "_rename_table_if_exists",
                autospec=True,
            ) as rename_table,
            patch.object(
                type(self.config),
                "_ensure_sequences",
                autospec=True,
            ) as ensure_sequences,
            patch.object(
                type(self.config),
                "_create_foreign_tables",
                autospec=True,
            ) as create_foreign,
            patch.object(
                type(self.config),
                "_recreate_auditlog_log_line_view",
                autospec=True,
            ) as recreate_view,
        ):
            self.config._swap_auditlog_tables_to_fdw()

        drop_view.assert_called_once_with(
            self.config, "public", "auditlog_log_line_view"
        )
        self.assertEqual(drop_foreign.call_count, 2)
        self.assertEqual(rename_table.call_count, 2)
        ensure_sequences.assert_called_once_with(self.config)
        create_foreign.assert_called_once_with(self.config, "public")
        recreate_view.assert_called_once_with(self.config, "public")

    def test_10_restore_auditlog_tables_from_backup_calls_expected_helpers(self):
        with (
            patch.object(
                type(self.config),
                "_drop_view_if_exists",
                autospec=True,
            ) as drop_view,
            patch.object(
                type(self.config),
                "_drop_foreign_table_if_exists",
                autospec=True,
            ) as drop_foreign,
            patch.object(
                type(self.config),
                "_rename_table_if_exists",
                autospec=True,
            ) as rename_table,
            patch.object(
                type(self.config),
                "_recreate_auditlog_log_line_view",
                autospec=True,
            ) as recreate_view,
        ):
            self.config._restore_auditlog_tables_from_backup()

        drop_view.assert_called_once_with(
            self.config, "public", "auditlog_log_line_view"
        )
        self.assertEqual(drop_foreign.call_count, 2)
        self.assertEqual(rename_table.call_count, 2)
        recreate_view.assert_called_once_with(self.config, "public")

    def test_11_healthcheck_success(self):
        with (
            patch.object(self.env.cr, "execute") as execute,
            patch.object(self.env.cr, "fetchone", return_value=(1,)),
        ):
            self.config._healthcheck_fdw_read()

        execute.assert_called_once()

    def test_12_healthcheck_raises_usererror_on_failure(self):
        original_execute = self.env.cr.execute

        def mocked_execute(query, params=None, log_exceptions=None):
            query_str = str(query)
            if "SELECT 1 FROM" in query_str and "auditlog_log" in query_str:
                raise Exception("fdw boom")
            return original_execute(query, params, log_exceptions=log_exceptions)

        with patch.object(self.env.cr, "execute", side_effect=mocked_execute):
            with self.assertRaises(UserError) as err:
                self.config._healthcheck_fdw_read()

        self.assertIn("cannot be read through PostgreSQL FDW", str(err.exception))
        self.assertIn("fdw boom", str(err.exception))
