# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import datetime

from datetime import timedelta

from odoo.addons.resource.models.resource import ResourceCalendar
from odoo.addons.resource.models.resource import to_naive_user_tz
from odoo.tools.float_utils import float_compare


def post_load_hook():

    def _new_schedule_days(self, days, day_dt, compute_leaves=False,
                           resource_id=None):
        if not hasattr(self, '_get_schedule_days_iteration_limit'):
            return self._schedule_days_original(
                days, day_dt, compute_leaves=compute_leaves,
                resource_id=resource_id)
        # START OF HOOK: Introduce here the iterations limit
        iterations_limit = self._get_schedule_days_iteration_limit() or 100
        # END OF HOOK
        backwards = (days < 0)
        intervals = []
        planned_days, iterations = 0, 0

        day_dt_tz = to_naive_user_tz(day_dt, self.env.user)
        current_datetime = day_dt_tz.replace(
            hour=0, minute=0, second=0, microsecond=0)

        # HOOK. Use the iterations_limit here
        while planned_days < abs(days) and iterations < iterations_limit:
            working_intervals = self._get_day_work_intervals(
                current_datetime.date(),
                compute_leaves=compute_leaves, resource_id=resource_id)
            if not self or working_intervals:
                # no calendar -> no working hours, but day is
                # considered as worked
                planned_days += 1
                intervals += working_intervals
            # get next day
            if backwards:
                current_datetime = self._get_previous_work_day(
                    current_datetime)
            else:
                current_datetime = self._get_next_work_day(current_datetime)
            # avoid infinite loops
            iterations += 1

        return intervals

    def _new_schedule_hours(self, hours, day_dt, compute_leaves=False,
                            resource_id=None):
        if not hasattr(self, '_get_schedule_hours_iteration_limit'):
            return self._schedule_hours_original(
                hours, day_dt, compute_leaves=compute_leaves,
                resource_id=resource_id)
        self.ensure_one()
        # START OF HOOK: Introduce here the iterations limit
        iterations_limit = self._get_schedule_hours_iteration_limit() or 1000
        # END OF HOOK
        backwards = (hours < 0)
        intervals = []
        remaining_hours, iterations = abs(hours * 1.0), 0

        day_dt_tz = to_naive_user_tz(day_dt, self.env.user)
        current_datetime = day_dt_tz

        call_args = dict(compute_leaves=compute_leaves,
                         resource_id=resource_id)

        # HOOK. Use the iterations_limit here
        while float_compare(remaining_hours, 0.0, precision_digits=2) in (
                1, 0) and iterations < iterations_limit:
            if backwards:
                call_args['end_time'] = current_datetime.time()
            else:
                call_args['start_time'] = current_datetime.time()

            working_intervals = self._get_day_work_intervals(
                current_datetime.date(), **call_args)

            if working_intervals:
                new_working_intervals = self._interval_schedule_hours(
                    working_intervals, remaining_hours, backwards=backwards)

                res = timedelta()
                for interval in working_intervals:
                    res += interval[1] - interval[0]
                remaining_hours -= res.total_seconds() / 3600.0

                intervals = intervals + new_working_intervals if \
                    not backwards else new_working_intervals + intervals
            # get next day
            if backwards:
                current_datetime = datetime.datetime.combine(
                    self._get_previous_work_day(current_datetime),
                    datetime.time(23, 59, 59))
            else:
                current_datetime = datetime.datetime.combine(
                    self._get_next_work_day(current_datetime),
                    datetime.time())
            # avoid infinite loops
            iterations += 1

        return intervals

    if not hasattr(ResourceCalendar, '_schedule_days_original'):
        ResourceCalendar._schedule_days_original = \
            ResourceCalendar._schedule_days

    ResourceCalendar._patch_method("_schedule_days", _new_schedule_days)

    if not hasattr(ResourceCalendar, '_schedule_hours_original'):
        ResourceCalendar._schedule_hours_original = \
            ResourceCalendar._schedule_hours

    ResourceCalendar._patch_method("_schedule_hours", _new_schedule_hours)
