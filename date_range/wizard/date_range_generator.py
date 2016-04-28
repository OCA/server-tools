# -*- coding: utf-8 -*-
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
from dateutil.rrule import (rrule,
                            YEARLY,
                            MONTHLY,
                            WEEKLY,
                            DAILY)
from dateutil.relativedelta import relativedelta


class DateRangeGenerator(models.TransientModel):
    _name = 'date.range.generator'

    @api.model
    def _default_company(self):
        return self.env['res.company']._company_default_get('date.range')

    name_prefix = fields.Char('Range name prefix', required=True)
    date_start = fields.Date(strint='Start date', required=True)
    type_id = fields.Many2one(
        comodel_name='date.range.type', string='Type', required=True,
        ondelete='cascade')
    company_id = fields.Many2one(
        comodel_name='res.company', string='Company',
        default=_default_company)
    unit_of_time = fields.Selection([
        (YEARLY, 'years'),
        (MONTHLY, 'months'),
        (WEEKLY, 'weeks'),
        (DAILY, 'days')], required=True)
    duration_count = fields.Integer('Duration', required=True)
    count = fields.Integer(
        string="Number of ranges to generate", required=True)

    @api.multi
    def _compute_date_ranges(self):
        self.ensure_one()
        vals = rrule(freq=self.unit_of_time, interval=self.duration_count,
                     dtstart=fields.Date.from_string(self.date_start),
                     count=self.count+1)
        vals = list(vals)
        date_ranges = []
        for idx, dt_start in enumerate(vals[:-1]):
            date_start = fields.Date.to_string(dt_start.date())
            # always remove 1 day for the date_end since range limits are
            # inclusive
            dt_end = vals[idx+1].date() - relativedelta(days=1)
            date_end = fields.Date.to_string(dt_end)
            date_ranges.append({
                'name': '%s-%d' % (self.name_prefix, idx + 1),
                'date_start': date_start,
                'date_end': date_end,
                'type_id': self.type_id.id,
                'company_id': self.company_id.id})
        return date_ranges

    @api.multi
    def action_apply(self):
        date_ranges = self._compute_date_ranges()
        if date_ranges:
            for dr in date_ranges:
                self.env['date.range'].create(dr)
        return self.env['ir.actions.act_window'].for_xml_id(
            module='date_range', xml_id='date_range_action')
