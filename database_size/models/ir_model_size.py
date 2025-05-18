# Copyright 2025 Opener B.V. <https://opener.amsterdam>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from datetime import timedelta

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class IrModelSize(models.Model):
    _name = "ir.model.size"
    _description = "Disk space usage per model"
    _order = "measurement_date desc, total_model_size desc"
    _rec_name = "model"
    _sql_constraints = [
        (
            "uniq_model_measurement_date",
            "unique(model, measurement_date)",
            "There is already a measurement for this model on the given date",
        ),
    ]
    model = fields.Char(index=True)
    model_name = fields.Char(
        compute="_compute_model_name",
        store=True,
    )
    measurement_date = fields.Date(
        "Date of Measurement",
        help="For the exact time, check the record's write_date.",
        required=True,
    )
    total_model_size = fields.Integer(
        compute="_compute_total_sizes",
        help="Total model size in MB. This includes attachments.",
        store=True,
    )
    total_database_size = fields.Integer(
        compute="_compute_total_sizes",
        help="Total Model Size in MB. This includes many2many tables",
        store=True,
    )
    total_table_size = fields.Integer(
        help="Total Table Size in MB. This includes indexes and toast tables",
    )
    table_size = fields.Integer(
        string="Bare Table Size",
        help="Bare Table Size in MB.",
    )
    ir_model_index_size_ids = fields.One2many(
        comodel_name="ir.model.index.size",
        inverse_name="ir_model_size_id",
        string="Indexes",
    )
    ir_model_relation_size_ids = fields.One2many(
        comodel_name="ir.model.relation.size",
        inverse_name="ir_model_size_id",
        string="Relations",
    )
    indexes_size = fields.Integer(
        compute="_compute_indexes_size",
        help="Total Size of Indexes in MB",
        store=True,
        string="Index Size",
    )
    relations_size = fields.Integer(
        compute="_compute_relations_size",
        help="Total Size of many2many relations in MB",
        store=True,
        string="Many2many Tables Size",
    )
    tuples = fields.Integer(
        string="Estimated Rows",
        help="Rows in use, including dead tuples",
    )
    attachment_size = fields.Integer(
        help=(
            "Attachment Size in MB. Includes overlap of files that are also "
            "attached to other models."
        ),
    )

    @api.depends("model")
    def _compute_model_name(self):
        """Assign the model's label"""
        model2name = {
            model.model: model.name for model in self.env["ir.model"].sudo().search([])
        }
        for size in self:
            size.model_name = model2name.get(size.model, "<removed>")

    @api.model
    def read_group(
        self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True
    ):
        """Enforce that grouped results are ordered.

        Odoo will happily use the grouping field for ordering unless groupby is a
        list, and as it happens the grouping is usually passed as a list, for
        example: ['measurement_date:day']
        """
        if not orderby and groupby and isinstance(groupby, list | set):
            field = groupby[0].split(":")[0]
            orderby = f"{field} desc"
        return super().read_group(
            domain,
            fields,
            groupby,
            offset=offset,
            limit=limit,
            orderby=orderby,
            lazy=lazy,
        )

    @api.depends(
        "total_table_size",
        "relations_size",
        "attachment_size",
    )
    def _compute_total_sizes(self):
        for size in self:
            size.total_database_size = size.total_table_size + size.relations_size
            size.total_model_size = size.total_database_size + size.attachment_size

    @api.depends("ir_model_index_size_ids", "ir_model_index_size_ids.size")
    def _compute_indexes_size(self):
        for size in self:
            size.indexes_size = sum(size.ir_model_index_size_ids.mapped("size"))

    @api.depends("ir_model_relation_size_ids", "ir_model_relation_size_ids.size")
    def _compute_relations_size(self):
        for size in self:
            size.relations_size = sum(size.ir_model_relation_size_ids.mapped("size"))

    @staticmethod
    def _normalize_size(size):
        """Filter out -1s and compute as MB"""
        if not size:
            return 0
        return int(max(0, size) / (1024 * 1024))

    @api.model
    def _measure(self):
        """Create the entries for today's report"""
        today = fields.Date.context_today(self)
        # Remove any previous report for the same day
        self.search([("measurement_date", "=", today)]).unlink()
        table2model = {}
        for model in self.env.values():
            if not model._abstract and not model._transient:
                model_model = model._name
                table2model[model._table] = model_model
        model2vals = {
            model_model: {
                "model": model_model,
                "measurement_date": today,
                "ir_model_index_size_ids": [],
                "ir_model_relation_size_ids": [],
            }
            for model_model in table2model.values()
        }
        # Some many2many relation objects are linked explicitely to both models
        # involved. To prevent counting them double, we will link them to the
        # largest table. Gather all the related models first.
        self.env.cr.execute(
            """
            select name, array_agg(model)
            from ir_model_relation group by name;
            """
        )
        relation2model = dict(self.env.cr.fetchall())
        self.env.cr.execute(
            """
            SELECT relname,
                reltuples,
                pg_total_relation_size (C.oid),
                pg_relation_size (C.oid)
            FROM pg_class C
                LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace)
            WHERE nspname NOT IN (
                'information_schema',
                'pg_catalog',
                'pg_logical',
                'pg_toast'
            )
            AND C.relkind = 'r'
            """
        )
        # Gather sizes of model tables and many2many tables
        rows = self.env.cr.fetchall()
        for table, tuples, total_table_size, table_size in rows:
            model = table2model.get(table)
            if model:
                model2vals[model].update(
                    {
                        "table_size": self._normalize_size(table_size),
                        "total_table_size": self._normalize_size(total_table_size),
                        "tuples": max(tuples, 0),
                    }
                )
        # Second pass to throw in the relation tables with the largest relation
        for table, _tuples, total_table_size, _table_size in rows:
            if table in relation2model:
                models = relation2model[table]
                model = sorted(
                    models,
                    key=lambda model: model2vals.get(model, {"tuples": -99})["tuples"],
                    reverse=True,
                )[0]
                vals = model2vals.get(model)
                if vals:
                    vals["ir_model_relation_size_ids"].append(
                        fields.Command.create(
                            {
                                "name": table,
                                "size": self._normalize_size(total_table_size),
                            }
                        )
                    )
        # Gather sizes of indexes
        self.env.cr.execute(
            """
            SELECT i.relname table_name,
                indexrelname index_name,
                pg_relation_size(indexrelid) index_size
            FROM pg_stat_all_indexes i
            JOIN pg_class c ON i.relid=c.oid
            WHERE schemaname NOT IN (
                'information_schema',
                'pg_catalog',
                'pg_toast',
                'pg_logical'
            );
            """
        )
        for table, index, size in self.env.cr.fetchall():
            vals = model2vals.get(table2model.get(table))
            if vals:
                vals["ir_model_index_size_ids"].append(
                    fields.Command.create(
                        {
                            "name": index,
                            "size": self._normalize_size(size),
                        }
                    )
                )
        # Gather sizes of attachments. Deduplicate by checksum such that the
        # attachment is attributed to the first model it was linked to.
        self.env.cr.execute(
            """
            with unique_attachments as (
                select res_model,
                    file_size,
                    row_number() over (partition by checksum order by id) as rowno
                    from ir_attachment
                )
            select res_model, sum(file_size)
            from unique_attachments
            where rowno = 1
            group by res_model;
            """
        )
        for model, size in self.env.cr.fetchall():
            vals = model2vals.get(model)
            if vals:
                vals["attachment_size"] = self._normalize_size(size)
        vals_list = [val for val in model2vals.values() if "table_size" in val]
        self.create(vals_list)
        _logger.info("Created %s model database size records", len(vals_list))

    @api.autovacuum
    def _purge(self):
        """Remove older model size records, if enabled in the General Settings."""
        if (
            not self.env["ir.config_parameter"]
            .sudo()
            .get_param("database_size.purge_enable")
        ):
            return
        retention_daily = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("database_size.retention_daily", 366)
        )
        retention_monthly = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("database_size.retention_monthly", 0)
        )
        if retention_daily:
            cutoff_date = fields.Date.today() - timedelta(days=retention_daily)
            self.env.cr.execute(
                """
                delete from ir_model_size
                where measurement_date < %(cutoff_date)s
                and extract(day from measurement_date) != 1;
                """,
                {"cutoff_date": cutoff_date},
            )
            _logger.info(
                f"Deleted {self.env.cr.rowcount} ir_model_size from before "
                f"{cutoff_date} from any other day than the first day of the month."
            )
        if retention_monthly and retention_monthly > retention_daily:
            cutoff_date = fields.Date.today() - timedelta(days=retention_monthly)
            self.env.cr.execute(
                """
                delete from ir_model_size
                where measurement_date < %(cutoff_date)s;
                """,
                {"cutoff_date": cutoff_date},
            )
            _logger.info(
                f"Deleted {self.env.cr.rowcount} ir_model_size from before "
                f"{cutoff_date}."
            )
