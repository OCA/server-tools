# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    @api.multi
    def _get_schedule_days_iteration_limit(self):
        self.ensure_one()
        limit = self.env['ir.config_parameter'].sudo().get_param(
            'resource.calendar.schedule.days.iteration.limit', default=False)
        return int(limit) or False

    @api.multi
    def _get_schedule_hours_iteration_limit(self):
        self.ensure_one()
        limit = self.env['ir.config_parameter'].sudo().get_param(
            'resource.calendar.schedule.hours.iteration.limit', default=False)
        return int(limit) or False
