# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, tools


class TimeWeekday(models.Model):
    _name = "time.weekday"
    _description = "Time Week Day"

    name = fields.Selection(
        selection=[
            ("0", "Monday"),
            ("1", "Tuesday"),
            ("2", "Wednesday"),
            ("3", "Thursday"),
            ("4", "Friday"),
            ("5", "Saturday"),
            ("6", "Sunday"),
        ],
        required=True,
    )
    _sql_constraints = [("name_uniq", "UNIQUE(name)", ("Name must be unique"))]

    @api.depends("name")
    def _compute_display_name(self):
        """
        WORKAROUND since Odoo doesn't handle properly records where name is
        a selection
        """
        translated_values = dict(self._fields["name"]._description_selection(self.env))
        for record in self:
            record.display_name = translated_values[record.name]

    @api.model
    @tools.ormcache("name")
    def _get_id_by_name(self, name):
        return self.search([("name", "=", name)], limit=1).id

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        self.env.registry.clear_cache()
        return records

    def write(self, vals):
        result = super().write(vals)
        self.env.registry.clear_cache()
        return result

    def unlink(self):
        result = super().unlink()
        self.env.registry.clear_cache()
        return result

    def _get_next_weekday_date(self, date_from=False, include_date_from=True):
        """Returns the next Date matching weekday

        :param date_from: Date object from which we start searching for next weekday
        :param include_date_from: Allows to return date from if it's same weekday
        :return Date object matching the weekday
        """
        self.ensure_one()
        if not date_from:
            date_from = fields.Date.today()
        next_weekday_delta = int(self.name) - date_from.weekday()
        if next_weekday_delta < 0:
            next_weekday_delta += 7
        elif next_weekday_delta == 0 and not include_date_from:
            next_weekday_delta += 7
        return fields.Date.add(date_from, days=next_weekday_delta)

    def _get_next_weekdays_date(self, date_from=False, include_date_from=True):
        return min(
            [
                weekday._get_next_weekday_date(
                    date_from=date_from, include_date_from=include_date_from
                )
                for weekday in self
            ]
        )
