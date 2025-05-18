# Copyright 2025 Opener B.V. <https://opener.amsterdam>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import UserError


class IrModelSizeReport(models.Model):
    _name = "ir.model.size.report"
    _description = "Historical Disk space usage per model"
    _auto = False
    _rec_name = "historical_measurement_date"
    _order = "historical_measurement_date desc, diff_total_model_size desc"

    model = fields.Char()
    model_name = fields.Char()

    measurement_date = fields.Date("Date of Measurement")
    historical_measurement_date = fields.Date("Historical Date of Measurement")

    total_model_size = fields.Integer()
    historical_total_model_size = fields.Integer()
    diff_total_model_size = fields.Integer("Change in Total Model Size")

    total_database_size = fields.Integer()
    historical_total_database_size = fields.Integer()
    diff_total_database_size = fields.Integer("Change in Total Database Size")

    total_table_size = fields.Integer()
    historical_total_table_size = fields.Integer()

    table_size = fields.Integer("Bare Table Size")
    historical_table_size = fields.Integer("Historical Bare Table Size")

    indexes_size = fields.Integer("Index Size")
    historical_indexes_size = fields.Integer("Historical Index Size")

    relations_size = fields.Integer("Many2many Tables Size")
    historical_relations_size = fields.Integer("Historical Many2many Tables Size")

    tuples = fields.Integer("Estimated Rows")
    historical_tuples = fields.Integer("Historical Estimated Rows")

    attachment_size = fields.Integer()
    historical_attachment_size = fields.Integer()

    def action_open_model_sizes(self):
        """Open the model_sizes from the report line.

        At this point, the 'virtual' report record might not exist anymore
        so we fetch the dates from the context.
        """
        self.ensure_one()
        domain = [
            ("model", "=", self.model),
            (
                "measurement_date",
                "in",
                (
                    self.env.context.get("measurement_date"),
                    self.env.context.get("historical_measurement_date"),
                ),
            ),
        ]
        action = self.env["ir.actions.actions"]._for_xml_id(
            "database_size.ir_model_size_action"
        )
        action["domain"] = domain
        return action

    @api.model
    def _move_dates_to_context(self, domain):
        """Move the requested comparison date from the domain into the context.

        The values in the context will be used when creating the virtual table
        in `_table_query`.
        """
        new_domain = []
        values = {}
        for clause in domain or []:
            for field in ("measurement_date", "historical_measurement_date"):
                if not isinstance(clause, tuple | list) or clause[0] != field:
                    continue
                if field in values:
                    raise UserError(
                        self.env._(
                            f"You cannot search on more than one value for {field} "
                            "at the same time."
                        )
                    )
                if clause[1] in ("=", "==") and clause[2]:
                    values[field] = clause[2]
                else:
                    raise UserError(
                        self.env._(
                            f"Searching {field} for '{clause[1]} {clause[2]}' is "
                            "not supported."
                        )
                    )
                new_domain.append((1, "=", 1))
            else:
                new_domain.append(clause)
        if values:
            self = self.with_context(**values)
        return self, new_domain

    @api.model
    def _where_calc(self, domain, active_test=True):
        """Move the requested dates from the domain into the context"""
        (self, new_domain) = self._move_dates_to_context(domain)
        return super()._where_calc(new_domain, active_test=active_test)

    @api.model
    def search(self, domain, offset=0, limit=None, order=None):
        """Move the requested dates from the domain into the context"""
        (self, new_domain) = self._move_dates_to_context(domain)
        return super().search(new_domain, offset=offset, limit=limit, order=order)

    @api.model
    def search_count(self, domain, limit=None):
        """Move the requested dates from the domain into the context"""
        (self, new_domain) = self._move_dates_to_context(domain)
        return super().search_count(new_domain, limit=limit)

    @property
    def _table_query(self):
        """Report comparative database size changes between two dates.

        The dates are inserted in the context in this model's `search` method.
        """
        measurement_date = self.env.context.get("measurement_date")
        if measurement_date:
            measurement_date = fields.Date.to_date(measurement_date)
            if not self.env["ir.model.size"].search(
                [("measurement_date", "=", measurement_date)],
                limit=1,
            ):
                raise UserError(
                    self.env._(
                        "There is no data from "
                        f"{fields.Date.to_string(measurement_date)}"
                    )
                )
        else:
            # Use the most recent measurement by default
            measurement_date = (
                self.env["ir.model.size"]
                .search([], order="id desc", limit=1)
                .measurement_date
            )
            if not measurement_date:
                raise UserError(self.env._("There does not seem to be any data"))

        historical_measurement_date = self.env.context.get(
            "historical_measurement_date"
        )
        if historical_measurement_date:
            historical_measurement_date = fields.Date.to_date(
                historical_measurement_date
            )
            if not self.env["ir.model.size"].search(
                [("measurement_date", "=", historical_measurement_date)],
                limit=1,
            ):
                raise UserError(
                    self.env._(
                        "There is no data from "
                        f"{fields.Date.to_string(historical_measurement_date)}"
                    )
                )
        else:
            # Use last month by default
            last_month = measurement_date - relativedelta(months=1)
            historical_measurement_date = (
                self.env["ir.model.size"]
                .search(
                    [
                        ("measurement_date", ">=", last_month),
                        ("measurement_date", "<", measurement_date),
                    ],
                    order="measurement_date asc",
                    limit=1,
                )
                .measurement_date
            )
            if not historical_measurement_date:
                raise UserError(
                    self.env._("There does not seem to be enough data to compare")
                )

        return self.env.cr.mogrify(
            """
            select %(measurement_date)s as measurement_date,
            %(historical_measurement_date)s as historical_measurement_date,
            cur.id as id,
            cur.model,
            cur.model_name,
            cur.total_model_size,
            coalesce(hst.total_model_size, 0) as historical_total_model_size,
            coalesce(cur.total_model_size) - coalesce(hst.total_model_size, 0)
                as diff_total_model_size,

            cur.total_database_size,
            coalesce(hst.total_database_size, 0) as historical_total_database_size,
            coalesce(cur.total_database_size, 0) - coalesce(hst.total_database_size, 0)
                as diff_total_database_size,

            cur.table_size,
            coalesce(hst.table_size, 0) as historical_table_size,
            cur.total_table_size,
            coalesce(hst.total_table_size, 0) as historical_total_table_size,
            cur.indexes_size,
            coalesce(hst.indexes_size, 0) as historical_indexes_size,
            cur.relations_size,
            coalesce(hst.relations_size, 0) as historical_relations_size,
            cur.tuples,
            coalesce(hst.tuples, 0) as historical_tuples,
            cur.attachment_size,
            coalesce(hst.attachment_size, 0) as historical_attachment_size

            from ir_model_size cur
            left join ir_model_size hst
            on cur.model = hst.model
                and hst.measurement_date = %(historical_measurement_date)s
            where cur.measurement_date = %(measurement_date)s
            """,
            {
                "measurement_date": measurement_date,
                "historical_measurement_date": historical_measurement_date,
            },
        ).decode("utf-8")
