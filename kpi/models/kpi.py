# -*- coding: utf-8 -*-
# Copyright 2012 - Now Savoir-faire Linux <https://www.savoirfairelinux.com/>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta
from openerp import fields, models, api
from openerp.tools.safe_eval import safe_eval
from openerp.tools import (
    DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT,
)
import re
import logging
_logger = logging.getLogger(__name__)


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


class KPI(models.Model):
    """Key Performance Indicators."""

    _name = "kpi"
    _description = "Key Performance Indicator"

    name = fields.Char('Name', required=True)
    description = fields.Text('Description')
    category_id = fields.Many2one(
        'kpi.category',
        'Category',
        required=True,
    )
    threshold_id = fields.Many2one(
        'kpi.threshold',
        'Threshold',
        required=True,
    )
    periodicity = fields.Integer('Periodicity', default=1)

    periodicity_uom = fields.Selection((
        ('hour', 'Hour'),
        ('day', 'Day'),
        ('week', 'Week'),
        ('month', 'Month')
    ), 'Periodicity UoM', required=True, default='day')

    next_execution_date = fields.Datetime(
        'Next execution date',
        readonly=True,
    )
    value = fields.Float(string='Value',
                         compute="_compute_display_last_kpi_value",
                         )
    kpi_type = fields.Selection((
        ('python', 'Python'),
        ('local', 'SQL - Local DB'),
        ('external', 'SQL - External DB')
    ), 'KPI Computation Type')

    dbsource_id = fields.Many2one(
        'base.external.dbsource',
        'External DB Source',
    )
    kpi_code = fields.Text(
        'KPI Code',
        help=("SQL code must return the result as 'value' "
              "(i.e. 'SELECT 5 AS value')."),
    )
    history_ids = fields.One2many(
        'kpi.history',
        'kpi_id',
        'History',
    )
    active = fields.Boolean(
        'Active',
        help=("Only active KPIs will be updated by the scheduler based on"
              " the periodicity configuration."), default=True
    )
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env.user.company_id.id)

    @api.multi
    def _compute_display_last_kpi_value(self):
        history_obj = self.env['kpi.history']
        for obj in self:
            history_ids = history_obj.search([("kpi_id", "=", obj.id)])
            if history_ids:
                obj.value = obj.history_ids[0].value
            else:
                obj.value = 0

    @api.multi
    def compute_kpi_value(self):
        for obj in self:
            kpi_value = 0
            if obj.kpi_code:
                if obj.kpi_type == 'local' and is_sql_or_ddl_statement(
                        obj.kpi_code):
                    self.env.cr.execute(obj.kpi_code)
                    dic = self.env.cr.dictfetchall()
                    if is_one_value(dic):
                        kpi_value = dic[0]['value']
                elif (obj.kpi_type == 'external' and obj.dbsource_id.id and
                      is_sql_or_ddl_statement(obj.kpi_code)):
                    dbsrc_obj = obj.dbsource_id
                    res = dbsrc_obj.execute(obj.kpi_code)
                    if is_one_value(res):
                        kpi_value = res[0]['value']
                elif obj.kpi_type == 'python':
                    kpi_value = safe_eval(obj.kpi_code)

            threshold_obj = obj.threshold_id
            values = {
                'kpi_id': obj.id,
                'value': kpi_value,
                'color': threshold_obj.get_color(kpi_value),
            }
            history_obj = self.env['kpi.history']
            history_obj.create(values)
        return True

    @api.multi
    def update_next_execution_date(self):
        for obj in self:
            if obj.periodicity_uom == 'hour':
                delta = timedelta(hours=obj.periodicity)
            elif obj.periodicity_uom == 'day':
                delta = timedelta(days=obj.periodicity)
            elif obj.periodicity_uom == 'week':
                delta = timedelta(weeks=obj.periodicity)
            elif obj.periodicity_uom == 'month':
                delta = timedelta(months=obj.periodicity)
            else:
                delta = timedelta()
            new_date = datetime.now() + delta

            obj.next_execution_date = new_date.strftime(DATETIME_FORMAT)

        return True

    # Method called by the scheduler
    @api.model
    def update_kpi_value(self):
        filters = [
            '&',
            '|',
            ('active', '=', True),
            ('next_execution_date', '<=', datetime.now().strftime(
                DATETIME_FORMAT)),
            ('next_execution_date', '=', False),
        ]
        if 'filters' in self.env.context:
            filters.extend(self.env.context['filters'])
        obj_ids = self.search(filters)
        res = None

        try:
            for obj in obj_ids:
                obj.compute_kpi_value()
                obj.update_next_execution_date()
        except Exception:
            _logger.exception("Failed updating KPI values")

        return res
