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

from openerp import fields, models, api
from openerp.tools.safe_eval import safe_eval
import re


def is_one_value(result):
    # check if sql query returns only one value
    if type(result) is dict and 'value' in result.dictfetchone():
        return True
    elif type(result) is list and 'value' in result[0]:
        return True
    else:
        return False


RE_SELECT_QUERY = re.compile('.*(' + '|'.join((
    'INSERT',
    'UPDATE',
    'DELETE',
    'CREATE',
    'ALTER',
    'DROP',
    'GRANT',
    'REVOKE',
    'INDEX',
)) + ')')


def is_sql_or_ddl_statement(query):
    """Check if sql query is a SELECT statement"""
    return not RE_SELECT_QUERY.match(query.upper())


class KPIThresholdRange(models.Model):
    """
    KPI Threshold Range
    """
    _name = "kpi.threshold.range"
    _description = "KPI Threshold Range"

    name = fields.Char('Name', size=50, required=True)
    valid = fields.Boolean(string='Valid', required=True,
                           compute="_compute_is_valid_range", default=True)
    invalid_message = fields.Char(string='Message', size=100,
                                  compute="_compute_generate_invalid_message")
    min_type = fields.Selection((
        ('static', 'Fixed value'),
        ('python', 'Python Code'),
        ('local', 'SQL - Local DB'),
        ('external', 'SQL - Externa DB'),
    ), 'Min Type', required=True)
    min_value = fields.Float(string='Minimum', compute="_compute_min_value")
    min_fixed_value = fields.Float('Minimum')
    min_code = fields.Text('Minimum Computation Code')
    min_dbsource_id = fields.Many2one(
        'base.external.dbsource',
        'External DB Source',
    )
    max_type = fields.Selection((
        ('static', 'Fixed value'),
        ('python', 'Python Code'),
        ('local', 'SQL - Local DB'),
        ('external', 'SQL - External DB'),
    ), 'Max Type', required=True)
    max_value = fields.Float(string='Maximum', compute="_compute_max_value")
    max_fixed_value = fields.Float('Maximum')
    max_code = fields.Text('Maximum Computation Code')
    max_dbsource_id = fields.Many2one(
        'base.external.dbsource',
        'External DB Source',
    )

    color = fields.Char(
        string="Color",
        help="Choose your color"
    )

    threshold_ids = fields.Many2many(
        'kpi.threshold',
        'kpi_threshold_range_rel',
        'range_id',
        'threshold_id',
        'Thresholds',
    )
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env.user.company_id.id)

    @api.multi
    def _compute_min_value(self):
        result = {}
        for obj in self:
            value = None
            if obj.min_type == 'local' and is_sql_or_ddl_statement(
                    obj.min_code):
                self.env.cr.execute(obj.min_code)
                dic = self.env.cr.dictfetchall()
                if is_one_value(dic):
                    value = dic[0]['value']
            elif (obj.min_type == 'external' and obj.min_dbsource_id.id and
                  is_sql_or_ddl_statement(obj.min_code)):
                dbsrc_obj = obj.min_dbsource_id
                res = dbsrc_obj.execute(obj.min_code)
                if is_one_value(res):
                    value = res[0]['value']
            elif obj.min_type == 'python':
                value = safe_eval(obj.min_code)
            else:
                value = obj.min_fixed_value
            result[obj.id] = value
        return result

    @api.multi
    def _compute_max_value(self):
        result = {}
        for obj in self:
            value = None
            if obj.max_type == 'local' and is_sql_or_ddl_statement(
                    obj.max_code):
                self.env.cr.execute(obj.max_code)
                dic = self.env.cr.dictfetchall()
                if is_one_value(dic):
                    value = dic[0]['value']
            elif obj.max_type == 'python':
                value = safe_eval(obj.max_code)
            elif (obj.max_type == 'external' and obj.max_dbsource_id.id and
                  is_sql_or_ddl_statement(obj.max_code)):
                dbsrc_obj = obj.max_dbsource_id
                res = dbsrc_obj.execute(obj.max_code)
                if is_one_value(res):
                    value = res[0]['value']
            else:
                value = obj.max_fixed_value
            result[obj.id] = value
        return result

    @api.multi
    def _compute_is_valid_range(self):
        result = {}
        for obj in self:
            if obj.max_value < obj.min_value:
                result[obj.id] = False
            else:
                result[obj.id] = True
        return result

    @api.multi
    def _compute_generate_invalid_message(self):
        result = {}
        for obj in self:
            if obj.valid:
                result[obj.id] = ""
            else:
                result[obj.id] = ("Minimum value is greater than the maximum "
                                  "value! Please adjust them.")
        return result
