# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
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

from openerp import fields, models, api, exceptions, _


class KPIThreshold(models.Model):
    """KPI Threshold."""

    _name = "kpi.threshold"
    _description = "KPI Threshold"

    @api.multi
    def _compute_is_valid_threshold(self):
        result = {}
        for obj in self:
            # check if ranges overlap
            # TODO: This code can be done better
            for range1 in obj.range_ids:
                for range2 in obj.range_ids:
                    if (range1.valid and range2.valid and
                            range1.min_value < range2.min_value):
                        result[obj.id] = range1.max_value <= range2.min_value
        return result

    @api.multi
    def _compute_generate_invalid_message(self):
        result = {}
        for obj in self:
            if obj.valid:
                result[obj.id] = ""
            else:
                result[obj.id] = ("2 of your ranges are overlapping! Please "
                                  "make sure your ranges do not overlap.")
        return result

    name = fields.Char('Name', size=50, required=True)
    range_ids = fields.Many2many(
        'kpi.threshold.range',
        'kpi_threshold_range_rel',
        'threshold_id',
        'range_id',
        'Ranges'
    )
    valid = fields.Boolean(string='Valid', required=True,
                           compute="_compute_is_valid_threshold", default=True)
    invalid_message = fields.Char(string='Message', size=100,
                                  compute="_compute_generate_invalid_message")
    kpi_ids = fields.One2many('kpi', 'threshold_id', 'KPIs')
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env.user.company_id.id)

    @api.model
    def create(self, data):
        # check if ranges overlap
        # TODO: This code can be done better
        range_obj1 = self.env['kpi.threshold.range']
        range_obj2 = self.env['kpi.threshold.range']
        if data.get('range_ids'):
            for range1 in data['range_ids'][0][2]:
                range_obj1 = range_obj1.browse(range1)
                for range2 in data['range_ids'][0][2]:
                    range_obj2 = range_obj2.browse(range2)
                    if (range_obj1.valid and range_obj2.valid and
                            range_obj1.min_value < range_obj2.min_value):
                        if range_obj1.max_value > range_obj2.min_value:
                            raise exceptions.Warning(
                                _("2 of your ranges are overlapping!"),
                                _("Make sure your ranges do not overlap!")
                            )
                    range_obj2 = self.env['kpi.threshold.range']
                range_obj1 = self.env['kpi.threshold.range']
        return super(KPIThreshold, self).create(data)

    @api.multi
    def get_color(self, kpi_value):
        color = '#FFFFFF'
        for obj in self:
            for range_obj in obj.range_ids:
                if (range_obj.min_value <= kpi_value <= range_obj.max_value and
                        range_obj.valid):
                    color = range_obj.color
        return color
