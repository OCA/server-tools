# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import math

from psycopg2.extensions import AsIs

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class DeliveryWindow(models.Model):

    _name = "delivery.window"
    _description = "Delivery Window"
    _order = "partner_id, start"

    start = fields.Float("From", required=True)
    end = fields.Float("To", required=True)
    week_day_ids = fields.Many2many(
        comodel_name="alc.delivery.week.day", required=True
    )
    partner_id = fields.Many2one(
        "res.partner", required=True, index=True, ondelete='cascade'
    )

    @api.constrains("start", "end", "week_day_ids")
    def check_window_no_onverlaps(self):
        week_days_field = self._fields["week_day_ids"]
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
                    AND d.%(relation_week_day_fkey)s in %(week_day_ids)s
                    AND w.partner_id = %(partner_id)s"""
            self.env.cr.execute(
                SQL,
                dict(
                    table=AsIs(self._table),
                    relation=AsIs(week_days_field.relation),
                    relation_window_fkey=AsIs(week_days_field.column1),
                    relation_week_day_fkey=AsIs(week_days_field.column2),
                    start=record.start,
                    end=record.end,
                    window_id=record.id,
                    week_day_ids=tuple(record.week_day_ids.ids),
                    partner_id=record.partner_id.id,
                ),
            )
            res = self.env.cr.fetchall()
            if res:
                other = self.browse(res[0][0])
                raise ValidationError(
                    _("%s overlaps %s")
                    % (record.display_name, other.display_name)
                )

    @api.depends("start", "end", "week_day_ids")
    def _compute_display_name(self):
        for record in self:
            "{days}: From {start} to {end}".format(
                days=", ".join(record.week_day_ids.mapped("display_name")),
                start=self.float_to_time_repr(record.start),
                end=self.float_to_time_repr(record.end),
            )

    @api.model
    def float_to_time_repr(self, value):
        pattern = "%02d:%02d"
        hour = math.floor(value)
        min = round((value % 1) * 60)
        if min == 60:
            min = 0
            hour += 1

        return pattern % (hour, min)
