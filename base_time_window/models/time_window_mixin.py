# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import math
from datetime import time

from psycopg2.extensions import AsIs

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.misc import format_time


class TimeWindowMixin(models.AbstractModel):

    _name = "time.window.mixin"
    _description = "Time Window"
    _order = "time_window_start"

    # TODO patch api.constrains with field here?
    _time_window_overlap_check_field = False

    time_window_start = fields.Float("From", required=True)
    time_window_end = fields.Float("To", required=True)
    time_window_weekday_ids = fields.Many2many(
        comodel_name="time.weekday", required=True
    )

    @api.constrains("time_window_start", "time_window_end", "time_window_weekday_ids")
    def check_window_no_overlaps(self):
        weekdays_field = self._fields["time_window_weekday_ids"]
        for record in self:
            if record.time_window_start > record.time_window_end:
                raise ValidationError(
                    _("%s must be > %s")
                    % (
                        self.float_to_time_repr(record.time_window_end),
                        self.float_to_time_repr(record.time_window_start),
                    )
                )
            if not record.time_window_weekday_ids:
                raise ValidationError(_("At least one time.weekday is required"))
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
                    NUMRANGE(w.time_window_start::numeric,
                        w.time_window_end::numeric) &&
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
                    start=record.time_window_start,
                    end=record.time_window_end,
                    window_id=record.id,
                    weekday_ids=tuple(record.time_window_weekday_ids.ids),
                    check_field=AsIs(self._time_window_overlap_check_field),
                    check_field_id=record[self._time_window_overlap_check_field].id,
                ),
            )
            res = self.env.cr.fetchall()
            if res:
                other = self.browse(res[0][0])
                raise ValidationError(
                    _("%s overlaps %s") % (record.display_name, other.display_name)
                )

    @api.depends("time_window_start", "time_window_end", "time_window_weekday_ids")
    def _compute_display_name(self):
        for record in self:
            record.display_name = _("{days}: From {start} to {end}").format(
                days=", ".join(record.time_window_weekday_ids.mapped("display_name")),
                start=format_time(self.env, record.get_time_window_start_time()),
                end=format_time(self.env, record.get_time_window_end_time()),
            )

    @api.constrains("time_window_start", "time_window_end")
    def _check_window_under_twenty_four_hours(self):
        error_msg = _("Hour should be between 00 and 23")
        for record in self:
            if record.time_window_start:
                hour, minute = self._get_hour_min_from_value(record.time_window_start)
                if hour > 23:
                    raise ValidationError(error_msg)
            if record.time_window_end:
                hour, minute = self._get_hour_min_from_value(record.time_window_end)
                if hour > 23:
                    raise ValidationError(error_msg)

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

    def get_time_window_start_time(self):
        return self.float_to_time(self.time_window_start)

    def get_time_window_end_time(self):
        return self.float_to_time(self.time_window_end)
