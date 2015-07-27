# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 AKRETION (<http://www.akretion.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import fields, models, api, _
from openerp.exceptions import Warning
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime, timedelta


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    @api.model
    def _get_date(self, start_date, delay, resource_id=False):
        """This method gives the first date after a delay from the start date
            considering the working time attached to the company calendar.
        """
        if isinstance(start_date, str):
            start_date = fields.Date.from_string(start_date)
        if not self.id:
            model = self._context['params']['model']
            obj_id = self._context['params']['id']
            obj = self.env[model].browse(obj_id)
            self = obj.company_id.calendar_id
            if not self:
                raise Warning(_('Error !'), _(
                    'You need to define a calendar for the company !'))
        dt_leave = self.get_leave_intervals(
            resource_id, start_datetime=None, end_datetime=None)
        worked_days = (
            [day['dayofweek'] for day in self.attendance_ids])
        if delay < 0:
            delta = -1
        else:
            delta = 1
        while datetime.strftime(
            start_date, DEFAULT_SERVER_DATE_FORMAT) in dt_leave or str(
                start_date.weekday()) not in worked_days:
            start_date = start_date + timedelta(days=delta)
        date = start_date
        while delay:
            date = date + timedelta(days=delta)
            if datetime.strftime(
                date, DEFAULT_SERVER_DATE_FORMAT) not in dt_leave and str(
                    date.weekday()) in worked_days:
                delay = delay - delta
        return date
