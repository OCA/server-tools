# © 2022 initOS GmbH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ScheduleWeekday(models.Model):
    _name = "schedule.weekday"
    _description = "A weekday for selection in schedules"

    name = fields.Char(required=True, translate=True)
    number = fields.Integer(required=True)
