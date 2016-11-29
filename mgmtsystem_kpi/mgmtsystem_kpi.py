#  -*- encoding: utf-8 -*-
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

from datetime import datetime, timedelta
from openerp import fields
from openerp.tools.translate import _
from openerp.tools.safe_eval import safe_eval
from openerp.tools import (
    DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT,
)
import time
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


def is_select_query(query):
    """Check if sql query is a SELECT statement"""
    return not RE_SELECT_QUERY.match(query.upper())


class mgmtsystem_kpi_category(models.Model):
    """
    KPI Category
    """
    _name = "mgmtsystem.kpi.category"
    _description = "KPI Category"
    _columns = {
        'name': fields.char('Name', size=50, required=True),
        'description': fields.text('Description')
    }


class mgmtsystem_kpi_threshold_range(models.Model):
    """
    KPI Threshold Range
    """
    _name = "mgmtsystem.kpi.threshold.range"
    _description = "KPI Threshold Range"

    def compute_min_value(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        result = {}
        for obj in self.browse(cr, uid, ids):
            value = None
            if obj.min_type == 'local' and is_select_query(obj.min_code):
                cr.execute(obj.min_code)
                dic = cr.dictfetchall()
                if is_one_value(dic):
                    value = dic[0]['value']
            elif (obj.min_type == 'external'
                  and obj.min_dbsource_id.id
                  and is_select_query(obj.min_code)):
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

    def compute_max_value(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        result = {}
        for obj in self.browse(cr, uid, ids, context):
            value = None
            if obj.max_type == 'local' and is_select_query(obj.max_code):
                cr.execute(obj.max_code)
                dic = cr.dictfetchall()
                if is_one_value(dic):
                    value = dic[0]['value']
            elif obj.max_type == 'python':
                value = safe_eval(obj.max_code)
            elif (obj.max_type == 'external'
                  and obj.max_dbsource_id.id
                  and is_select_query(obj.max_code)):
                dbsrc_obj = obj.max_dbsource_id
                res = dbsrc_obj.execute(obj.max_code)
                if is_one_value(res):
                    value = res[0]['value']
            else:
                value = obj.max_fixed_value
            result[obj.id] = value
        return result

    def _is_valid_range(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        result = {}
        for obj in self.browse(cr, uid, ids, context):
            if obj.max_value < obj.min_value:
                result[obj.id] = False
            else:
                result[obj.id] = True
        return result

    def _generate_invalid_message(
            self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        result = {}
        for obj in self.browse(cr, uid, ids, context):
            if obj.valid:
                result[obj.id] = ""
            else:
                result[obj.id] = ("Minimum value is greater than the maximum "
                                  "value! Please adjust them.")
        return result

    _columns = {
        'name': fields.char('Name', size=50, required=True),
        'valid': fields.function(
            _is_valid_range,
            string='Valid',
            type='boolean',
            required=True,
        ),
        'invalid_message': fields.function(
            _generate_invalid_message,
            string='Message',
            type='char',
            size=100,
        ),
        'min_type': fields.selection((
            ('static', 'Fixed value'),
            ('python', 'Python Code'),
            ('local', 'SQL - Local DB'),
            ('external', 'SQL - Externa DB'),
        ), 'Min Type', required=True),
        'min_value': fields.function(
            compute_min_value,
            string='Minimum',
            type='float',
        ),
        'min_fixed_value': fields.float('Minimum'),
        'min_code': fields.text('Minimum Computation Code'),
        'min_dbsource_id': fields.many2one(
            'base.external.dbsource',
            'External DB Source',
        ),
        'max_type': fields.selection((
            ('static', 'Fixed value'),
            ('python', 'Python Code'),
            ('local', 'SQL - Local DB'),
            ('external', 'SQL - External DB'),
        ), 'Max Type', required=True),
        'max_value': fields.function(
            compute_max_value,
            string='Maximum',
            type='float',
        ),
        'max_fixed_value': fields.float('Maximum'),
        'max_code': fields.text('Maximum Computation Code'),
        'max_dbsource_id': fields.many2one(
            'base.external.dbsource',
            'External DB Source',
        ),
        'color': fields.char(
            'Color',
            help='RGB code with #',
            size=7,
            required=True,
        ),
        'threshold_ids': fields.many2many(
            'mgmtsystem.kpi.threshold',
            'mgmtsystem_kpi_threshold_range_rel',
            'range_id',
            'threshold_id',
            'Thresholds',
        ),
        'company_id': fields.many2one('res.company', 'Company')
    }

    _defaults = {
        'company_id': (
            lambda self, cr, uid, c:
            self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id),
        'valid': True,
    }


class mgmtsystem_kpi_threshold(models.Model):
    """
    KPI Threshold
    """
    _name = "mgmtsystem.kpi.threshold"
    _description = "KPI Threshold"

    def _is_valid_threshold(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        result = {}
        for obj in self.browse(cr, uid, ids, context):
            # check if ranges overlap
            # TODO: This code can be done better
            for range1 in obj.range_ids:
                for range2 in obj.range_ids:
                    if (range1.valid and range2.valid
                            and range1.min_value < range2.min_value):
                        result[obj.id] = range1.max_value <= range2.min_value
        return result

    def _generate_invalid_message(
            self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        result = {}
        for obj in self.browse(cr, uid, ids, context):
            if obj.valid:
                result[obj.id] = ""
            else:
                result[obj.id] = ("2 of your ranges are overlapping! Please "
                                  "make sure your ranges do not overlap.")
        return result

    _columns = {
        'name': fields.char('Name', size=50, required=True),
        'range_ids': fields.many2many(
            'mgmtsystem.kpi.threshold.range',
            'mgmtsystem_kpi_threshold_range_rel',
            'threshold_id',
            'range_id',
            'Ranges'
        ),
        'valid': fields.function(
            _is_valid_threshold,
            string='Valid',
            type='boolean',
            required=True,
        ),
        'invalid_message': fields.function(
            _generate_invalid_message,
            string='Message',
            type='char',
            size=100,
        ),
        'kpi_ids': fields.one2many('mgmtsystem.kpi', 'threshold_id', 'KPIs'),
        'company_id': fields.many2one('res.company', 'Company')
    }

    _defaults = {
        'company_id': (
            lambda self, cr, uid, c:
            self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id),
        'valid': True,
    }

    def create(self, cr, uid, data, context=None):
        if context is None:
            context = {}

        # check if ranges overlap
        # TODO: This code can be done better
        range_obj1 = self.pool.get('mgmtsystem.kpi.threshold.range')
        range_obj2 = self.pool.get('mgmtsystem.kpi.threshold.range')
        for range1 in data['range_ids'][0][2]:
            range_obj1 = range_obj1.browse(cr, uid, range1, context)
            for range2 in data['range_ids'][0][2]:
                range_obj2 = range_obj2.browse(cr, uid, range2, context)
                if (range_obj1.valid and range_obj2.valid
                        and range_obj1.min_value < range_obj2.min_value):
                    if range_obj1.max_value > range_obj2.min_value:
                        raise models.except_orm(
                            _("2 of your ranges are overlapping!"),
                            _("Please make sure your ranges do not overlap!")
                        )
                range_obj2 = self.pool.get('mgmtsystem.kpi.threshold.range')
            range_obj1 = self.pool.get('mgmtsystem.kpi.threshold.range')
        return super(mgmtsystem_kpi_threshold, self).create(
            cr, uid, data, context
        )

    def get_color(self, cr, uid, ids, kpi_value, context=None):
        if context is None:
            context = {}

        color = '#FFFFFF'
        for obj in self.browse(cr, uid, ids, context):
            for range_obj in obj.range_ids:
                if (range_obj.min_value <= kpi_value <= range_obj.max_value
                        and range_obj.valid):
                    color = range_obj.color
        return color


class mgmtsystem_kpi_history(models.Model):
    """
    History of the KPI
    """
    _name = "mgmtsystem.kpi.history"
    _description = "History of the KPI"

    _columns = {
        'name': fields.char('Name', size=150, required=True),
        'kpi_id': fields.many2one('mgmtsystem.kpi', 'KPI', required=True),
        'date': fields.datetime(
            'Execution Date',
            required=True,
            readonly=True,
        ),
        'value': fields.float('Value', required=True, readonly=True),
        'color': fields.text('Color', required=True, readonly=True),
        'company_id': fields.many2one('res.company', 'Company')
    }

    _defaults = {
        'company_id': (
            lambda self, cr, uid, c:
            self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id),
        'name': lambda *a: time.strftime('%d %B %Y'),
        'date': lambda *a: time.strftime(DATETIME_FORMAT),
        'color': '#FFFFFF',
    }

    _order = "date desc"


class mgmtsystem_kpi(models.Model):
    """
    Key Performance Indicators
    """
    _name = "mgmtsystem.kpi"
    _description = "Key Performance Indicator"

    def _display_last_kpi_value(
            self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}

        result = {}
        for obj in self.browse(cr, uid, ids):
            if obj.history_ids:
                result[obj.id] = obj.history_ids[0].value
            else:
                result[obj.id] = 0

        return result

    def compute_kpi_value(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for obj in self.browse(cr, uid, ids):
            kpi_value = 0
            if obj.kpi_type == 'local' and is_select_query(obj.kpi_code):
                cr.execute(obj.kpi_code)
                dic = cr.dictfetchall()
                if is_one_value(dic):
                    kpi_value = dic[0]['value']
            elif (obj.kpi_type == 'external'
                    and obj.dbsource_id.id
                    and is_select_query(obj.kpi_code)):
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

            history_obj = self.pool.get('mgmtsystem.kpi.history')
            history_id = history_obj.create(cr, uid, values, context=context)
            obj.history_ids.append(history_id)

        return True

    def update_next_execution_date(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        for obj in self.browse(cr, uid, ids):
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

            values = {
                'next_execution_date': new_date.strftime(DATETIME_FORMAT),
            }

            obj.write(values)

        return True

    # Method called by the scheduler
    def update_kpi_value(self, cr, uid, ids=None, context=None):
        if context is None:
            context = {}
        if not ids:
            filters = [
                '&',
                '|',
                ('active', '=', True),
                ('next_execution_date', '<=',
                    datetime.now().strftime(DATETIME_FORMAT)),
                ('next_execution_date', '=', False),
            ]
            if 'filters' in context:
                filters.extend(context['filters'])
            ids = self.search(cr, uid, filters, context=context)
        res = None

        try:
            res = self.compute_kpi_value(cr, uid, ids, context=context)
            self.update_next_execution_date(cr, uid, ids, context=context)
        except Exception:
            _logger.exception("Failed updating KPI values")

        return res

    _columns = {
        'name': fields.char('Name', size=50, required=True),
        'description': fields.text('Description'),
        'category_id': fields.many2one(
            'mgmtsystem.kpi.category',
            'Category',
            required=True,
        ),
        'threshold_id': fields.many2one(
            'mgmtsystem.kpi.threshold',
            'Threshold',
            required=True,
        ),
        'periodicity': fields.integer('Periodicity'),
        'periodicity_uom': fields.selection((
            ('hour', 'Hour'),
            ('day', 'Day'),
            ('week', 'Week'),
            ('month', 'Month')
        ), 'Periodicity UoM', required=True),
        'next_execution_date': fields.datetime(
            'Next execution date',
            readonly=True,
        ),
        'value': fields.function(
            _display_last_kpi_value,
            string='Value',
            type='float',
        ),
        'kpi_type': fields.selection((
            ('python', 'Python'),
            ('local', 'SQL - Local DB'),
            ('external', 'SQL - External DB')
        ), 'KPI Computation Type'),
        'dbsource_id': fields.many2one(
            'base.external.dbsource',
            'External DB Source',
        ),
        'kpi_code': fields.text(
            'KPI Code',
            help=("SQL code must return the result as 'value' "
                  "(i.e. 'SELECT 5 AS value')."),
        ),
        'history_ids': fields.one2many(
            'mgmtsystem.kpi.history',
            'kpi_id',
            'History',
        ),
        'active': fields.boolean(
            'Active',
            help=("Only active KPIs will be updated by the scheduler based on"
                  " the periodicity configuration."),
        ),
        'company_id': fields.many2one('res.company', 'Company')
    }

    _defaults = {
        'company_id': (
            lambda self, cr, uid, c:
            self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id),
        'active': True,
        'periodicity': 1,
        'periodicity_uom': 'day',
    }
