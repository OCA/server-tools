# Copyright (C) 2026 Cetmix OÜ
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools import SQL

_logger = logging.getLogger(__name__)


class AuditlogClickhouseConfig(models.Model):
    """Configure auditlog read mode through PostgreSQL FDW.

    This extension adds a switchable read mode on top of the active
    ClickHouse write configuration:

    - FDW read OFF -> Odoo reads regular PostgreSQL auditlog tables.
    - FDW read ON  -> Odoo reads ClickHouse through FOREIGN TABLE objects.

    The write pipeline remains controlled by auditlog_clickhouse_write.
    This model only manages runtime DDL required for reading.
    """

    _inherit = "auditlog.clickhouse.config"

    AUDITLOG_SCHEMA = "public"
    LOG_TABLE = "auditlog_log"
    FDW_SERVER = "auditlog_clickhouse_srv"
    LOG_LINE_TABLE = "auditlog_log_line"
    LOG_TABLE_BACKUP = "auditlog_log_pg_backup"
    LOG_LINE_TABLE_BACKUP = "auditlog_log_line_pg_backup"
    LOG_LINE_VIEW = "auditlog_log_line_view"

    _FDW_LOCKED_FIELDS = {"host", "port", "database", "user", "password"}

    fdw_enabled = fields.Boolean(
        string="FDW read enabled",
        readonly=True,
        help=(
            "Technical flag showing whether auditlog is currently read through "
            "PostgreSQL foreign tables backed by ClickHouse."
        ),
    )

    def write(self, vals):
        """Validate FDW-related safeguards before updating configuration.

        Blocks configuration changes that would leave auditlog read mode in an
        inconsistent or unsupported state.

        :param dict vals: Values to write on the configuration recordset.
        :return: Result of the parent ``write`` call.
        :rtype: bool
        :raises UserError: If the requested update is forbidden while FDW read
            is enabled.
        """
        self._check_fdw_write_constraints(vals)
        return super().write(vals)

    def unlink(self):
        """Prevent deleting configuration records while FDW read is enabled.

        :return: Result of the parent ``unlink`` call.
        :rtype: bool
        :raises UserError: If any record in ``self`` has ``fdw_enabled=True``.
        """
        if self.filtered("fdw_enabled"):
            raise UserError(
                self.env._(
                    "You cannot delete a ClickHouse configuration while FDW read "
                    "is enabled. Disable FDW read first."
                )
            )
        return super().unlink()

    def _check_fdw_write_constraints(self, vals):
        """Validate configuration changes that may break active FDW read mode.

        The method protects the following cases:

        - deactivating a configuration while FDW read is enabled;
        - activating another configuration while some other active configuration
          already has FDW read enabled;
        - changing connection parameters while FDW read is enabled.

        :param dict vals: Values passed to ``write()``.
        :raises UserError: If the requested modification is not allowed.
        """
        if vals.get("is_active") is False and self.filtered("fdw_enabled"):
            raise UserError(
                self.env._(
                    "You cannot deactivate a ClickHouse configuration while FDW "
                    "read is enabled. Disable FDW read first."
                )
            )

        if vals.get("is_active") is True:
            other_fdw_config = self.search(
                [
                    ("id", "not in", self.ids),
                    ("is_active", "=", True),
                    ("fdw_enabled", "=", True),
                ],
                limit=1,
            )
            if other_fdw_config:
                raise UserError(
                    self.env._(
                        "Another active ClickHouse configuration already has FDW "
                        "read enabled: %(config)s. Disable FDW read there first.",
                        config=other_fdw_config.display_name,
                    )
                )

        if self._FDW_LOCKED_FIELDS.intersection(vals) and self.filtered("fdw_enabled"):
            raise UserError(
                self.env._(
                    "You cannot change ClickHouse connection parameters while FDW "
                    "read is enabled. Disable FDW read first."
                )
            )

    @api.model
    def _relation_kind(self, schema, name):
        """Return PostgreSQL relation kind for a fully qualified object name.

        The value comes from ``pg_class.relkind`` and is used to determine
        whether a relation is a regular table, foreign table, view, or missing.

        :param str schema: PostgreSQL schema name.
        :param str name: Relation name inside the schema.
        :return: Relation kind code, or ``None`` if the relation does not exist.
        :rtype: str | None
        """
        self.env.cr.execute("SELECT to_regclass(%s)", (f"{schema}.{name}",))
        row = self.env.cr.fetchone()
        regclass_name = row[0] if row else None
        if not regclass_name:
            return None

        self.env.cr.execute(
            """
            SELECT c.relkind
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = %s
              AND c.relname = %s
            """,
            (schema, name),
        )
        row = self.env.cr.fetchone()
        return row[0] if row else None

    @api.model
    def _describe_relation_kind(self, kind):
        """Return a human-readable label for a PostgreSQL relation kind.

        :param str | None kind: Value of ``pg_class.relkind`` or ``None``.
        :return: Human-readable relation type label.
        :rtype: str
        """
        labels = {
            None: "missing",
            "r": "regular table",
            "f": "foreign table",
            "v": "view",
        }
        return labels.get(kind, f"unexpected relation ({kind})")

    @api.model
    def _get_auditlog_read_mode(self):
        """Detect the current auditlog read mode from PostgreSQL relations.

        Mode detection is based on relation kinds of
        ``auditlog_log`` and ``auditlog_log_line``:

        - ``"fdw"`` when both are foreign tables;
        - ``"postgres"`` when both are regular tables;
        - ``"mixed"`` for any inconsistent combination.

        :return: Current auditlog read mode.
        :rtype: str
        """
        schema = self.AUDITLOG_SCHEMA
        log_kind = self._relation_kind(schema, self.LOG_TABLE)
        line_kind = self._relation_kind(schema, self.LOG_LINE_TABLE)

        if log_kind == "f" and line_kind == "f":
            return "fdw"
        if log_kind == "r" and line_kind == "r":
            return "postgres"
        return "mixed"

    @api.model
    def _backup_tables_exist(self):
        """Check whether both PostgreSQL auditlog backup tables exist.

        :return: ``True`` if both backup tables are present as regular tables.
        :rtype: bool
        """
        schema = self.AUDITLOG_SCHEMA
        return (
            self._relation_kind(schema, self.LOG_TABLE_BACKUP) == "r"
            and self._relation_kind(schema, self.LOG_LINE_TABLE_BACKUP) == "r"
        )

    @api.model
    def _any_backup_object_exists(self):
        """Check whether any auditlog backup relation already exists.

        This helper is used before enabling FDW read to avoid colliding with
        stale backup objects left from an interrupted or manual operation.

        :return: ``True`` if at least one backup relation exists.
        :rtype: bool
        """
        schema = self.AUDITLOG_SCHEMA
        return bool(
            self._relation_kind(schema, self.LOG_TABLE_BACKUP)
            or self._relation_kind(schema, self.LOG_LINE_TABLE_BACKUP)
        )

    @api.model
    def _raise_inconsistent_schema_state(self):
        """Raise a detailed error for a mixed or corrupted auditlog schema state.

        The message contains the detected state of main and backup relations to
        help the operator understand what must be fixed before continuing.

        :raises UserError: Always, with details about current PostgreSQL objects.
        """
        schema = self.AUDITLOG_SCHEMA
        state = {
            self.LOG_TABLE: self._describe_relation_kind(
                self._relation_kind(schema, self.LOG_TABLE)
            ),
            self.LOG_LINE_TABLE: self._describe_relation_kind(
                self._relation_kind(schema, self.LOG_LINE_TABLE)
            ),
            self.LOG_TABLE_BACKUP: self._describe_relation_kind(
                self._relation_kind(schema, self.LOG_TABLE_BACKUP)
            ),
            self.LOG_LINE_TABLE_BACKUP: self._describe_relation_kind(
                self._relation_kind(schema, self.LOG_LINE_TABLE_BACKUP)
            ),
        }
        raise UserError(
            self.env._(
                "Auditlog read mode is in an inconsistent PostgreSQL state.\n\n"
                "%(log_table)s: %(log_state)s\n"
                "%(line_table)s: %(line_state)s\n"
                "%(log_backup)s: %(log_backup_state)s\n"
                "%(line_backup)s: %(line_backup_state)s\n\n"
                "Fix the schema state manually or restore a consistent mode "
                "before trying again.",
                log_table=self.LOG_TABLE,
                log_state=state[self.LOG_TABLE],
                line_table=self.LOG_LINE_TABLE,
                line_state=state[self.LOG_LINE_TABLE],
                log_backup=self.LOG_TABLE_BACKUP,
                log_backup_state=state[self.LOG_TABLE_BACKUP],
                line_backup=self.LOG_LINE_TABLE_BACKUP,
                line_backup_state=state[self.LOG_LINE_TABLE_BACKUP],
            )
        )

    def action_enable_fdw_read(self):
        """Enable FDW-based auditlog reading from ClickHouse.

        The method validates the current state, prepares FDW objects, swaps
        local PostgreSQL tables with foreign tables, performs a healthcheck,
        and finally synchronizes the technical ``fdw_enabled`` flag.

        :return: Standard client notification action.
        :rtype: dict
        :raises UserError: If the configuration is not active, the schema state
            is inconsistent, stale backup objects exist, or FDW setup fails.
        """
        self.ensure_one()

        if not self.is_active:
            raise UserError(
                self.env._(
                    "Only the active ClickHouse configuration can enable FDW read."
                )
            )

        read_mode = self._get_auditlog_read_mode()
        if read_mode == "fdw":
            self._set_fdw_enabled_flag(True)
            return self._notify(
                title=self.env._("Nothing to do"),
                message=self.env._("FDW read is already enabled."),
                notif_type="info",
            )
        if read_mode == "mixed":
            self._raise_inconsistent_schema_state()

        if self._any_backup_object_exists():
            raise UserError(
                self.env._(
                    "Cannot enable FDW read because backup auditlog tables already "
                    "exist. Clean the stale backup objects first."
                )
            )

        self._ensure_pg_clickhouse_extension()
        self._create_or_update_fdw_server()
        self._create_or_update_fdw_user_mapping()
        self._swap_auditlog_tables_to_fdw()
        self._healthcheck_fdw_read()

        self._set_fdw_enabled_flag(True)
        _logger.info("auditlog_clickhouse_read: FDW read enabled (config=%s)", self.id)
        return self._notify(
            title=self.env._("Success"),
            message=self.env._("FDW read is enabled for auditlog."),
            notif_type="success",
        )

    def action_disable_fdw_read(self):
        """Disable FDW-based auditlog reading and restore PostgreSQL tables.

        The method validates the current mode, restores local backup tables,
        recreates the SQL view, and synchronizes the technical flag.

        :return: Standard client notification action.
        :rtype: dict
        :raises UserError: If the schema state is inconsistent or required
            PostgreSQL backup tables are missing.
        """
        self.ensure_one()

        read_mode = self._get_auditlog_read_mode()
        if read_mode == "postgres":
            self._set_fdw_enabled_flag(False)
            return self._notify(
                title=self.env._("Nothing to do"),
                message=self.env._("FDW read is already disabled."),
                notif_type="info",
            )
        if read_mode == "mixed":
            self._raise_inconsistent_schema_state()

        if not self._backup_tables_exist():
            raise UserError(
                self.env._(
                    "Cannot disable FDW read because PostgreSQL backup tables are "
                    "missing. Partial rollback is not allowed."
                )
            )

        self._restore_auditlog_tables_from_backup()
        self._set_fdw_enabled_flag(False)
        _logger.info("auditlog_clickhouse_read: FDW read disabled (config=%s)", self.id)
        return self._notify(
            title=self.env._("Success"),
            message=self.env._(
                "FDW read is disabled and PostgreSQL tables were restored."
            ),
            notif_type="success",
        )

    def _set_fdw_enabled_flag(self, enabled):
        """Synchronize the technical FDW flag with the actual schema state.

        :param bool enabled: Target value for ``fdw_enabled``.
        :return: ``None``
        :rtype: None
        """
        if self.fdw_enabled == enabled:
            return
        super().write({"fdw_enabled": enabled})

    def _ensure_pg_clickhouse_extension(self):
        """Ensure the ``pg_clickhouse`` extension exists in PostgreSQL.

        :raises UserError: If PostgreSQL fails to create or load the extension.
        """
        try:
            self.env.cr.execute("CREATE EXTENSION IF NOT EXISTS pg_clickhouse")
        except Exception as exc:
            self._raise_fdw_setup_error(
                self.env._("Failed to initialize pg_clickhouse extension"),
                exc,
            )

    def _create_or_update_fdw_server(self):
        """Create or update the PostgreSQL foreign server definition.

        The server points PostgreSQL FDW reads to the configured ClickHouse
        instance and database.

        :raises UserError: If host is missing or the server DDL fails.
        """
        driver = "binary"
        host = (self.host or "").strip()
        if not host:
            raise UserError(self.env._("Host is required."))

        port = str(int(self.port or 0) or self.DEFAULT_PORT)
        dbname = (self.database or "").strip() or self.DEFAULT_DB

        try:
            if self._fdw_server_exists():
                self.env.cr.execute(
                    SQL(
                        """
                        ALTER SERVER %s OPTIONS (
                            SET driver %s,
                            SET host %s,
                            SET port %s,
                            SET dbname %s
                        )
                        """,
                        SQL.identifier(self.FDW_SERVER),
                        driver,
                        host,
                        port,
                        dbname,
                    )
                )
            else:
                self.env.cr.execute(
                    SQL(
                        """
                        CREATE SERVER %s
                        FOREIGN DATA WRAPPER clickhouse_fdw
                        OPTIONS (
                            driver %s,
                            host %s,
                            port %s,
                            dbname %s
                        )
                        """,
                        SQL.identifier(self.FDW_SERVER),
                        driver,
                        host,
                        port,
                        dbname,
                    )
                )
        except Exception as exc:
            self._raise_fdw_setup_error(
                self.env._("Failed to create or update the FDW server"),
                exc,
            )

    def _create_or_update_fdw_user_mapping(self):
        """Create or update the user mapping for the current PostgreSQL user.

        The mapping stores ClickHouse credentials used by PostgreSQL FDW when
        querying foreign tables.

        :raises UserError: If PostgreSQL fails to create or update the mapping.
        """
        ch_user = (self.user or "default").strip() or "default"
        ch_password = self.password or ""

        try:
            if self._fdw_user_mapping_exists():
                self.env.cr.execute(
                    SQL(
                        """
                        ALTER USER MAPPING FOR CURRENT_USER
                        SERVER %s
                        OPTIONS (
                            SET user %s,
                            SET password %s
                        )
                        """,
                        SQL.identifier(self.FDW_SERVER),
                        ch_user,
                        ch_password,
                    )
                )
            else:
                self.env.cr.execute(
                    SQL(
                        """
                        CREATE USER MAPPING FOR CURRENT_USER
                        SERVER %s
                        OPTIONS (
                            user %s,
                            password %s
                        )
                        """,
                        SQL.identifier(self.FDW_SERVER),
                        ch_user,
                        ch_password,
                    )
                )
        except Exception as exc:
            self._raise_fdw_setup_error(
                self.env._("Failed to create or update the FDW user mapping"),
                exc,
            )

    def _raise_fdw_setup_error(self, message, exc):
        """Raise a normalized user-facing error for FDW setup failures.

        For PostgreSQL privilege errors, the method returns a more explicit DBA
        instruction. Other errors are wrapped into a generic ``UserError``.

        :param str message: Human-readable operation context.
        :param Exception exc: Original exception raised during FDW setup.
        :raises UserError: Always, with a normalized message for the UI.
        """
        if getattr(exc, "pgcode", None) == "42501":
            raise UserError(
                self.env._(
                    "%(message)s.\n\n"
                    "The current PostgreSQL user does not have enough privileges.\n"
                    "Ask your DBA to grant:\n"
                    "- USAGE on foreign-data wrapper clickhouse_fdw;\n"
                    "- USAGE on foreign server %(server)s;\n"
                    "- CREATE and USAGE on schema %(schema)s.\n\n"
                    "Original error: %(error)s",
                    message=message,
                    server=self.FDW_SERVER,
                    schema=self.AUDITLOG_SCHEMA,
                    error=str(exc),
                )
            ) from exc

        raise UserError(
            self.env._("%(message)s: %(error)s", message=message, error=str(exc))
        ) from exc

    @api.model
    def _fdw_server_exists(self):
        """Check whether the PostgreSQL foreign server already exists.

        :return: ``True`` if the configured foreign server exists.
        :rtype: bool
        """
        self.env.cr.execute(
            "SELECT 1 FROM pg_foreign_server WHERE srvname = %s",
            (self.FDW_SERVER,),
        )
        return bool(self.env.cr.fetchone())

    @api.model
    def _fdw_user_mapping_exists(self):
        """Check whether a user mapping exists for ``CURRENT_USER``.

        :return: ``True`` if a mapping exists for the configured FDW server.
        :rtype: bool
        """
        self.env.cr.execute(
            "SELECT 1 FROM pg_user_mappings "
            "WHERE srvname = %s AND usename = current_user",
            (self.FDW_SERVER,),
        )
        return bool(self.env.cr.fetchone())

    @api.model
    def _drop_foreign_table_if_exists(self, schema, name):
        """Drop a foreign table when the target relation is an FDW object.

        :param str schema: PostgreSQL schema name.
        :param str name: Relation name to drop.
        """
        if self._relation_kind(schema, name) == "f":
            self.env.cr.execute(
                SQL(
                    "DROP FOREIGN TABLE %s.%s",
                    SQL.identifier(schema),
                    SQL.identifier(name),
                )
            )

    @api.model
    def _rename_table_if_exists(self, schema, name, new_name):
        """Rename a regular PostgreSQL table when it exists.

        :param str schema: PostgreSQL schema name.
        :param str name: Current table name.
        :param str new_name: Target table name.
        """
        if self._relation_kind(schema, name) == "r":
            self.env.cr.execute(
                SQL(
                    "ALTER TABLE %s.%s RENAME TO %s",
                    SQL.identifier(schema),
                    SQL.identifier(name),
                    SQL.identifier(new_name),
                )
            )

    @api.model
    def _drop_view_if_exists(self, schema, name):
        """Drop an SQL view if it exists.

        :param str schema: PostgreSQL schema name.
        :param str name: View name.
        """
        self.env.cr.execute(
            SQL(
                "DROP VIEW IF EXISTS %s.%s",
                SQL.identifier(schema),
                SQL.identifier(name),
            )
        )

    @api.model
    def _ensure_sequences(self):
        """Ensure auditlog sequences exist for the write pipeline.

        These sequences are required because auditlog rows written to
        ClickHouse still depend on PostgreSQL-generated integer identifiers.
        """
        self.env.cr.execute("CREATE SEQUENCE IF NOT EXISTS auditlog_log_id_seq")
        self.env.cr.execute("CREATE SEQUENCE IF NOT EXISTS auditlog_log_line_id_seq")

    def _create_foreign_tables(self, schema):
        """Create PostgreSQL foreign tables for auditlog data stored in ClickHouse.

        The created table schemas must match ORM expectations for
        ``auditlog.log`` and ``auditlog.log.line``.

        :param str schema: PostgreSQL schema where foreign tables must be created.
        """
        db_opt = (self.database or "").strip() or self.DEFAULT_DB

        self.env.cr.execute(
            SQL(
                """
                CREATE FOREIGN TABLE %s.%s (
                    id bigint,
                    create_date timestamp,
                    create_uid integer,
                    write_date timestamp,
                    write_uid integer,
                    name text,
                    model_id integer,
                    model_name text,
                    model_model text,
                    res_id bigint,
                    res_ids text,
                    user_id integer,
                    method text,
                    http_session_id integer,
                    http_request_id integer,
                    log_type text
                )
                SERVER %s
                OPTIONS (table_name %s, database %s)
                """,
                SQL.identifier(schema),
                SQL.identifier(self.LOG_TABLE),
                SQL.identifier(self.FDW_SERVER),
                self.LOG_TABLE,
                db_opt,
            )
        )

        self.env.cr.execute(
            SQL(
                """
                CREATE FOREIGN TABLE %s.%s (
                    id bigint,
                    create_date timestamp,
                    create_uid integer,
                    write_date timestamp,
                    write_uid integer,
                    field_id integer,
                    log_id bigint,
                    old_value text,
                    new_value text,
                    old_value_text text,
                    new_value_text text,
                    field_name text,
                    field_description text
                )
                SERVER %s
                OPTIONS (table_name %s, database %s)
                """,
                SQL.identifier(schema),
                SQL.identifier(self.LOG_LINE_TABLE),
                SQL.identifier(self.FDW_SERVER),
                self.LOG_LINE_TABLE,
                db_opt,
            )
        )

    @api.model
    def _recreate_auditlog_log_line_view(self, schema):
        """Recreate the SQL view used by ``auditlog.log.line.view``.

        The view is rebuilt against whichever auditlog relations are currently
        active: regular PostgreSQL tables or FDW foreign tables.

        :param str schema: PostgreSQL schema where the SQL view must be created.
        """
        self._drop_view_if_exists(schema, self.LOG_LINE_VIEW)
        self.env.cr.execute(
            SQL(
                """
                CREATE VIEW %s.%s AS
                SELECT alogl.id,
                       alogl.create_date,
                       alogl.create_uid,
                       alogl.write_uid,
                       alogl.write_date,
                       alogl.field_id,
                       alogl.log_id,
                       alogl.old_value,
                       alogl.new_value,
                       alogl.old_value_text,
                       alogl.new_value_text,
                       alogl.field_name,
                       alogl.field_description,
                       alog.name,
                       alog.model_id,
                       alog.model_name,
                       alog.model_model,
                       alog.res_id,
                       alog.user_id,
                       alog.method,
                       alog.http_session_id,
                       alog.http_request_id,
                       alog.log_type
                FROM %s.%s alogl
                JOIN %s.%s alog ON alog.id = alogl.log_id
                """,
                SQL.identifier(schema),
                SQL.identifier(self.LOG_LINE_VIEW),
                SQL.identifier(schema),
                SQL.identifier(self.LOG_LINE_TABLE),
                SQL.identifier(schema),
                SQL.identifier(self.LOG_TABLE),
            )
        )

    def _swap_auditlog_tables_to_fdw(self):
        """Replace local auditlog tables with FDW-backed foreign tables.

        The method preserves original PostgreSQL data by renaming the tables to
        backup names before creating foreign tables under the original names.
        """
        schema = self.AUDITLOG_SCHEMA
        self._drop_view_if_exists(schema, self.LOG_LINE_VIEW)
        self._drop_foreign_table_if_exists(schema, self.LOG_LINE_TABLE)
        self._drop_foreign_table_if_exists(schema, self.LOG_TABLE)
        self._rename_table_if_exists(
            schema,
            self.LOG_LINE_TABLE,
            self.LOG_LINE_TABLE_BACKUP,
        )
        self._rename_table_if_exists(
            schema,
            self.LOG_TABLE,
            self.LOG_TABLE_BACKUP,
        )
        self._ensure_sequences()
        self._create_foreign_tables(schema)
        self._recreate_auditlog_log_line_view(schema)

    @api.model
    def _restore_auditlog_tables_from_backup(self):
        """Restore original PostgreSQL auditlog tables from backup names.

        The method drops active foreign tables, renames backup tables back to
        their original names, and recreates the SQL view.
        """
        schema = self.AUDITLOG_SCHEMA
        self._drop_view_if_exists(schema, self.LOG_LINE_VIEW)
        self._drop_foreign_table_if_exists(schema, self.LOG_LINE_TABLE)
        self._drop_foreign_table_if_exists(schema, self.LOG_TABLE)
        self._rename_table_if_exists(
            schema,
            self.LOG_LINE_TABLE_BACKUP,
            self.LOG_LINE_TABLE,
        )
        self._rename_table_if_exists(
            schema,
            self.LOG_TABLE_BACKUP,
            self.LOG_TABLE,
        )
        self._recreate_auditlog_log_line_view(schema)

    @api.model
    def _healthcheck_fdw_read(self):
        """Verify that auditlog foreign tables are readable after FDW activation.

        The healthcheck performs a lightweight read against the active
        ``auditlog_log`` relation to ensure that PostgreSQL FDW and ClickHouse
        are reachable for auditlog UI reads.

        :raises UserError: If the foreign table cannot be queried.
        """
        try:
            self.env.cr.execute(
                SQL(
                    "SELECT 1 FROM %s.%s LIMIT 1",
                    SQL.identifier(self.AUDITLOG_SCHEMA),
                    SQL.identifier(self.LOG_TABLE),
                )
            )
            self.env.cr.fetchone()
        except Exception as exc:
            raise UserError(
                self.env._(
                    "FDW read activation failed because auditlog data cannot be "
                    "read through PostgreSQL FDW: %(error)s",
                    error=str(exc),
                )
            ) from exc
