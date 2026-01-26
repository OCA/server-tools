# Copyright 2025 Therp BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

import logging
from datetime import datetime, timedelta

from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from odoo import models
from odoo.sql_db import db_connect


class IrCron(models.Model):
    _inherit = "ir.cron"

    def _postgres_vacuum(self, max_minutes, full_vacuum):
        """
        Vacuum or analyze tables, don't continue after max_minutes have elapsed

        Do either a VACUUM FULL (full_vacuum=True) or ANALYZE
        """

        _logger = logging.getLogger("odoo.addons.postgres_vacuum")

        query = "ANALYZE (SKIP_LOCKED)"
        if full_vacuum:
            query = "VACUUM (FULL, SKIP_LOCKED)"

        current_time = datetime.now()
        exit_time_window = current_time + timedelta(minutes=max_minutes)

        order_by_clause = "last_analyze"
        if full_vacuum:
            order_by_clause = "last_vacuum"

        connection = db_connect(self.env.cr.dbname)

        with connection.cursor() as cr:
            cr._cnx.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            # pylint: disable=sql-injection
            cr.execute(f"SET statement_timeout = '{int(max_minutes)}min'")

            # pylint: disable=sql-injection
            cr.execute(
                f"""
                SELECT relname
                FROM pg_stat_user_tables
                ORDER BY {order_by_clause} ASC NULLS FIRST
                """
            )
            for (table,) in cr.fetchall():
                action = "vacuum" if full_vacuum else "analyze"

                if datetime.now() >= exit_time_window:
                    _logger.info(
                        "{max_minutes} minutes elapsed, not continuing to {action}"
                    )
                    return

                _logger.debug(f"{action} of table {table}")
                try:
                    # pylint: disable=sql-injection
                    cr.execute(f'{query} "{table}"')
                except Exception:
                    _logger.exception(f"{action} of table {table} failed")
                else:
                    _logger.debug(f"{action} of table {table} done")
