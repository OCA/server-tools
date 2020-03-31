# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import math
from datetime import time

from psycopg2.extensions import AsIs

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class TimeWindowMixin(models.AbstractModel):

    _name = "time.window.mixin"
    _description = "Time Window"
    _order = "start"

    # TODO patch api.constrains with field here?
    _overlap_check_field = False

    start = fields.Float("From", required=True)
    end = fields.Float("To", required=True)
    weekday_ids = fields.Many2many(
        comodel_name="time.weekday", required=True
    )

    @api.constrains("start", "end", "weekday_ids")
    def check_window_no_overlaps(self):
        weekdays_field = self._fields["weekday_ids"]
        for record in self:
            if record.start > record.end:
                raise ValidationError(
                    _("%s must be > %s")
                    % (
                        self.float_to_time_repr(record.end),
                        self.float_to_time_repr(record.start),
                    )
                )
            # here we use a plain SQL query to benefit of the numrange
            # function available in PostgresSQL
            # (http://www.postgresql.org/docs/current/static/rangetypes.html)
            SQL = """
                SELECT
                    id
                FROM
                    %(table)s w
                    join %(relation)s as d
                    on d.%(relation_window_fkey)s = w.id
                WHERE
                    NUMRANGE(w.start::numeric, w.end::numeric) &&
                        NUMRANGE(%(start)s::numeric, %(end)s::numeric)
                    AND w.id != %(window_id)s
                    AND d.%(relation_week_day_fkey)s in %(weekday_ids)s
                    AND w.%(check_field)s = %(check_field_id)s;"""
            self.env.cr.execute(
                SQL,
                dict(
                    table=AsIs(self._table),
                    relation=AsIs(weekdays_field.relation),
                    relation_window_fkey=AsIs(weekdays_field.column1),
                    relation_week_day_fkey=AsIs(weekdays_field.column2),
                    start=record.start,
                    end=record.end,
                    window_id=record.id,
                    weekday_ids=tuple(record.weekday_ids.ids),
                    check_field=AsIs(self._overlap_check_field),
                    check_field_id=record[self._overlap_check_field].id,
                ),
            )
            res = self.env.cr.fetchall()
            if res:
                other = self.browse(res[0][0])
                raise ValidationError(
                    _("%s overlaps %s")
                    % (record.display_name, other.display_name)
                )

    @api.depends("start", "end", "weekday_ids")
    def _compute_display_name(self):
        for record in self:
            record.display_name = _("{days}: From {start} to {end}").format(
                days=", ".join(record.weekday_ids.mapped("display_name")),
                start=self.float_to_time_repr(record.start),
                end=self.float_to_time_repr(record.end),
            )

    @api.model
    def _get_hour_min_from_value(self, value):
        hour = math.floor(value)
        minute = round((value % 1) * 60)
        if minute == 60:
            minute = 0
            hour += 1
        return hour, minute

    @api.model
    def float_to_time_repr(self, value):
        pattern = "%02d:%02d"
        hour, minute = self._get_hour_min_from_value(value)
        return pattern % (hour, minute)

    @api.model
    def float_to_time(self, value):
        hour, minute = self._get_hour_min_from_value(value)
        return time(hour=hour, minute=minute)

    def get_start_time(self):
        return self.float_to_time(self.start)

    def get_end_time(self):
        return self.float_to_time(self.end)
