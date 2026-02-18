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
    def _tune(self):
        vacuum_threshold = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "database_autovacuum_tuning.autovacuum_vacuum_max_threshold",
                default="100000",
            )
            or 100000
        )
        if vacuum_threshold <= 0:
            return
        analyze_threshold = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "database_autovacuum_tuning.autovacuum_vacuum_analyze_max_threshold",
                default="50000",
            )
            or 50000
        )
        query = """
            SELECT
                t.schemaname,
                t.tablename,
                st.dead_tuple_count
            FROM pg_tables AS t
            JOIN LATERAL pgstattuple(
                format('%%I.%%I', t.schemaname, t.tablename)::regclass
            ) AS st ON true
            WHERE t.tableowner = current_user
                AND t.schemaname = 'public'
                AND st.dead_tuple_count > %s
            ORDER BY t.schemaname, t.tablename
        """
        self.env.cr.execute(query, (vacuum_threshold,))
        results = self.env.cr.fetchall()
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
