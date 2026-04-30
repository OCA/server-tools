# Copyright 2026 Camptocamp (https://www.camptocamp.com).
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)


from odoo import api, fields, models


class DatabaseAutovacuumTuning(models.Model):
    _name = "database.autovacuum.tuning"
    _description = "Database Autovacuum Tuning"

    name = fields.Char(required=True, help="Table name")
    vacuum_threshold = fields.Integer()
    analyze_threshold = fields.Integer()

    @api.model
    def _db_autovacuum_tune(self):
        vacuum_threshold, analyze_threshold = self._get_thresholds()
        if vacuum_threshold <= 0:
            return
        results = self._get_tables_exceeding_dead_tuples(vacuum_threshold)
        for schemaname, tablename, _ in results:
            self.env.cr.execute(
                f"""
                ALTER TABLE {schemaname}.{tablename} SET (
                    autovacuum_vacuum_scale_factor = 0,
                    autovacuum_vacuum_threshold = %s,
                    autovacuum_analyze_scale_factor = 0,
                    autovacuum_analyze_threshold = %s
                )
                """,
                (vacuum_threshold, analyze_threshold),
            )
            self.sudo().create(
                {
                    "name": f"{schemaname}.{tablename}",
                    "vacuum_threshold": vacuum_threshold,
                    "analyze_threshold": analyze_threshold,
                }
            )

    def _get_tables_exceeding_dead_tuples(self, vacuum_threshold):
        query = """
            SELECT
                t.schemaname,
                t.tablename,
                st.n_dead_tup
            FROM pg_tables AS t
            JOIN pg_stat_all_tables AS st
                ON st.schemaname = t.schemaname
                AND st.relname = t.tablename
            WHERE t.tableowner = current_user
                AND t.schemaname = 'public'
                AND st.n_dead_tup > %s
            ORDER BY t.schemaname, t.tablename
        """
        self.env.cr.execute(query, (vacuum_threshold,))
        return self.env.cr.fetchall()

    def _get_thresholds(self):
        try:
            vacuum_threshold = int(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param(
                    "database_autovacuum_tuning.autovacuum_vacuum_max_threshold",
                    default="0",
                )
            )
        except ValueError:
            vacuum_threshold = 0

        try:
            analyze_threshold = int(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param(
                    "database_autovacuum_tuning.autovacuum_vacuum_analyze_max_threshold",
                    default="0",
                )
            )
        except ValueError:
            analyze_threshold = 0

        return vacuum_threshold, analyze_threshold
